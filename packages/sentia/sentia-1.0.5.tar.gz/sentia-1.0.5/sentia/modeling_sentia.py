from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Dict, Optional, Union
import torch
from torch import nn
import torch.nn as nn
import math
import sacrebleu
import torch.nn.functional as F
from transformers import PreTrainedModel
from torch.cuda.amp import autocast
from transformers import GPT2Model
from datasets import load_dataset
from tqdm import tqdm
import os
from transformers.modeling_outputs import BaseModelOutput, CausalLMOutput
import wandb
from sentia.utils.SENTIAFeedForward import SENTIAFF
from sentia.config_sentia import SENTIAConfig
from sentia.utils.MHA import SENTIAAttention
from rotary_embedding_torch import RotaryEmbedding
from nltk.translate.bleu_score import sentence_bleu
import warnings

class RMSNorm(nn.Module):
    def __init__(self, d, p=-1., eps=1e-8, bias=False):
        """
            Root Mean Square Layer Normalization
        :param d: model size
        :param p: partial RMSNorm, valid value [0, 1], default -1.0 (disabled)
        :param eps:  epsilon value, default 1e-8
        :param bias: whether use bias term for RMSNorm, disabled by
            default because RMSNorm doesn't enforce re-centering invariance.
        """
        super(RMSNorm, self).__init__()

        self.eps = eps
        self.d = d
        self.p = p
        self.bias = bias

        self.scale = nn.Parameter(torch.ones(d))
        self.register_parameter("scale", self.scale)

        if self.bias:
            self.offset = nn.Parameter(torch.zeros(d))
            self.register_parameter("offset", self.offset)

    def forward(self, x):
        if self.p < 0. or self.p > 1.:
            norm_x = x.norm(2, dim=-1, keepdim=True)
            d_x = self.d
        else:
            partial_size = int(self.d * self.p)
            partial_x, _ = torch.split(x, [partial_size, self.d - partial_size], dim=-1)

            norm_x = partial_x.norm(2, dim=-1, keepdim=True)
            d_x = partial_size

        rms_x = norm_x * d_x ** (-1. / 2)
        x_normed = x / (rms_x + self.eps)

        if self.bias:
            return self.scale * x_normed + self.offset

        return self.scale * x_normed

class SENTIAPreTrainedModel(PreTrainedModel):
    config_class = SENTIAConfig
    is_parallelizable = True
    supports_gradient_checkpointing = False
    def __init__(self, config, *args, **kwargs):
        super(SENTIAPreTrainedModel, self).__init__(config, *args, **kwargs)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
    @staticmethod
    def generate_causal_mask(x):
        """
        Generate a causal mask for autoregressive self-attention.

        Args:
            x (torch.Tensor): The input tensor of shape `(seq_length, hidden_dim)`.

        Returns:
            torch.Tensor: The causal mask of shape `(seq_length, seq_length)`.
        """
        seq_length = x.size(1)
        half_seq_length = seq_length // 2
        mask = torch.zeros(seq_length, seq_length, dtype=torch.bool, device=x.device)
        mask[:half_seq_length, :half_seq_length] = True
        return mask
    @staticmethod
    def generate_conversational_mask(x):
        seq_length = x.size(1)
        batch_size = x.size(0)
        mask = torch.ones(seq_length, seq_length, dtype=torch.bool, device=x.device)
        return mask
    def to(self, device: Optional[torch.device] = None, dtype: Optional[torch.dtype] = None, *args, **kwargs):
        if dtype == torch.float16:
            warnings.warn("This model uses cuda operations float16 does not support. Please load the model using a different dtype.")
        super().to(device, dtype, *args, **kwargs)
    @DeprecationWarning
    @staticmethod
    def generate_attention_mask(input_ids, padding_token_id):
        """
        Generate an attention mask that ignores padding tokens.
        
        Args:
            input_ids (torch.Tensor): Input tensor containing token indices.
            padding_token_id (int): Token ID of the padding token.
            
        Returns:
            attention_mask (torch.Tensor): Attention mask tensor with 1s in positions of non-padding tokens and 0s in padding positions.
        """
        attention_mask = (input_ids != padding_token_id).bool()
        return attention_mask
    def backward(self, loss, threshold=1e-6):
        """
        Backward pass of the SENTIA model with optional gradient pruning.

        Args:
            loss (torch.Tensor): Loss tensor.
            threshold (float, optional): Threshold value for gradient pruning. Defaults to 1e-6.
        """
        for p in self.parameters():
            if p.grad is not None and torch.max(torch.abs(p.grad)) < threshold:
                p.grad = None
        loss.backward()
    def save(self, directory):
        """
        Save the SENTIA model to a given directory.

        Args:
            model (nn.Module): The SENTIA model instance to save.
            directory (str): The directory path to save the model.

        Returns:
            None
        """
        model = self
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the model's state dictionary
        model_path = os.path.join(directory, 'sentia_model.bin')
        torch.save(model.state_dict(), model_path)

        print(f"Model saved at {model_path}")
    def load(self, directory):
        """
        Load the SENTIA model from a given directory.

        Args:
            model_class (nn.Module): The class of the SENTIA model to instantiate.
            directory (str): The directory path where the model is saved.

        Returns:
            model (nn.Module): The loaded SENTIA model.
        """
        # Instantiate the model
        model = self

        # Load the saved model's state dictionary
        try:
            model_path = os.path.join(directory, 'sentia_model.bin')
            model.load_state_dict(torch.load(model_path), strict=False)
        except Exception:
            model_path = os.path.join(directory, 'pytorch_model.bin')
            model.load_state_dict(torch.load(model_path), strict=False)

        print(f"Model loaded from {model_path}")

        return model
    @staticmethod
    def keytoken_weighted_loss(logits, inputs, keytoken_ids, alpha=1.0):
        # Calculate per-token loss
        loss_fct = nn.CrossEntropyLoss(reduce=False)
        loss = loss_fct(logits.view(-1, logits.size(-1)), inputs.view(-1))
        # Resize and average loss per sample
        loss_per_sample = loss.mean()
        # Calculate and scale weighting
        weights = torch.stack([(inputs == kt).float() for kt in keytoken_ids]).sum()
        weights = alpha * (1.0 + weights)
        # Calculate weighted average
        weighted_loss = (loss_per_sample * weights).mean()
        return weighted_loss
    def _generate(
            self,
            input_ids,
            temperature=0.6,
            top_k=50,
            top_p=0.92,
            max_length=20,
            repetition_penalty=1.176,
            device="cuda" if torch.cuda.is_available() else "cpu"
        ):
        warnings.warn("This method is deprecated, please use generate() instead")
        model = self
        model.eval()
        input_ids = input_ids.to(device)
        generated_text = input_ids.clone()  # Initialize with the provided input_ids

        for step in range(max_length):
            logits = model.forward(generated_text).logits  # Generate logits for the current input
            
            # Keep only the last token predictions of the first batch item (batch size 1), apply a temperature coefficient and filter
            logits = logits[0, -1, :] / temperature
            filtered_logits = self.top_k_top_p_filtering(logits, top_k=top_k, top_p=top_p)
            
            # Apply a minimum threshold for top-k filtering
            filtered_logits = self.apply_min_threshold(filtered_logits, min_threshold=0.1)
            
            # Apply repetition penalty to the logits
            if step > 0:
                for prev_token in generated_text[0]:
                    filtered_logits[prev_token] /= repetition_penalty
            
            # Sample the next token using multinomial distribution
            next_token_probs = F.softmax(filtered_logits, dim=-1)
            next_token_index = torch.multinomial(next_token_probs, 1)
            next_token = next_token_index.squeeze()
            
            # Append the next token to the generated text
            generated_text = torch.cat((generated_text, next_token.unsqueeze(0).unsqueeze(0)), dim=1)
            
            # Stop generating if the generated text reaches the desired max_length
            if generated_text.size(1) >= max_length:
                break

        return generated_text

    def _reorder_past(self, past, next_tokens):
        """
        Reorders the past state based on the selected next tokens.

        Args:
            past (tuple): Tuple containing the past states.
            next_tokens (torch.Tensor): Tensor containing the selected next tokens of shape (batch_size * num_beams).

        Returns:
            tuple: Reordered past state.
        """
        next_tokens = next_tokens.unsqueeze(-1).unsqueeze(-1)
        past = tuple([p.index_select(1, next_tokens[i].view(-1)) for i, p in enumerate(past)])
        return past
    @staticmethod
    def calculate_accuracy(predictions, targets):
        """
        Calculate the accuracy.

        Args:
            predictions (Tensor): Model predictions (e.g., logits).
            targets (Tensor): Ground truth labels.

        Returns:
            float: Accuracy.
        """
        predicted_classes = predictions
        correct_predictions = torch.sum(predicted_classes == targets).item()
        total_predictions = targets.size(0)  # Number of samples

        accuracy = correct_predictions / total_predictions
        return accuracy
    @staticmethod
    def apply_min_threshold(logits, min_threshold=0.1):
        # Apply a minimum threshold to logits to prevent very small values
        logits = torch.max(logits, torch.tensor(min_threshold).to(logits.device))
        return logits
    @staticmethod
    def nucleus_sampling(logits):
        # Perform nucleus sampling based on the logits
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        
        # Find the smallest index whose cumulative probability exceeds a threshold (0.95)
        nucleus_indices = cumulative_probs <= 0.95
        
        # Select the next token from nucleus sampling
        selected_index = torch.randint(0, nucleus_indices.size(1), (1,))
        next_token = sorted_indices[0, selected_index]
        
        return next_token
    @staticmethod
    def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
        """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
            Args:
                logits: logits distribution shape (vocabulary size)
                top_k >0: keep only top k tokens with highest probability (top-k filtering).
                top_p >0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                    Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        """
        logits = logits.squeeze(0)
        top_k = min(top_k, logits.size(-1))  # Safety check
        if top_k > 0:
            # Remove all tokens with a probability less than the last token of the top-k
            indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
            logits[indices_to_remove] = filter_value

        if top_p > 0.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probs > top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0

            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[indices_to_remove] = filter_value
        return logits
    def forward(self, x):
        raise NotImplementedError("The forward call of this model has not been implemented")
    # Will most likely will be deprecated in the future, you can create your own training loop, or use Trainer.
    @staticmethod
    def fit(model, num_epochs, dataloader, tokenizer, optimizer, val_dataloader, scheduler, device: torch.device, lr=4e-4):
        def lr_lambda(current_step):
            if current_step < 3000:
                return current_step / 3000
            return max(
                0.1,
                (num_epochs * len(dataloader) - current_step) / (num_epochs * len(dataloader) - 1500)
            )
        """
        Train the SENTIA model.

        Args:
            num_epochs (int): Number of training epochs.
            dataloader (DataLoader): Training data loader.
            model: The SENTIA model instance.
            tokenizer: Tokenizer for decoding predictions.
            optimizer: Optimizer for model parameter updates.
            val_dataloader (DataLoader): Validation data loader.
            scheduler: Learning rate scheduler.
        """
        keytoken_ids = []
        for keyword in [
            "plt",
            "pd",
            "sk",
            "fit",
            "predict",
            " plt",
            " pd",
            " sk",
            " fit",
            " predict",
            "testtest",
        ]:
            ids = tokenizer([keyword]).input_ids[0]
            if len(ids) == 1:
                keytoken_ids.append(ids[0])
            else:
                print(f"Keyword has not single token: {keyword}")
        model.to(device)
        optimizer = optimizer(model.parameters(), lr, eps=1e-4)
        scheduler = scheduler(optimizer, lr_lambda=lr_lambda)
        for epoch in range(num_epochs):
            model.train()
            print(f"Epoch {epoch+1}/{num_epochs}")
            total_loss = 0
            total_reward = 0
            total_bleu = 0
            total_perplexity = 0
            num_batches = 0
            accumulation_steps = 12  # Accumulate gradients over 12 batches
            predictions_list: list = []
            bleu_scores: list = []
            for i, batch in tqdm(enumerate(dataloader)):
                input_ids = batch["input_ids"].to(device)
                target_ids = batch["labels"].to(device)
                target_text = batch["target_text"]
                # Generate the output and calculate the loss
                outputs = model(input_ids=input_ids, labels=input_ids)
                loss, logits = outputs[:2]
                #loss = torch.exp(loss)
                # Calculate the BLEU score
                probs = F.softmax(logits, dim=-1)
                predictions = torch.argmax(probs, dim=-1)
                predictions_str = [tokenizer.decode(pred, skip_special_tokens=True) for pred in predictions.tolist()]
                target_ids_str = [tokenizer.decode(tgt, skip_special_tokens=True) for tgt in target_ids.tolist()]
                print(predictions_str[0])
                bleu_scores = []
                accuracy_scores = []
                for pred_str, target_str in zip(predictions_str, target_ids_str):
                    bleu = sacrebleu.sentence_bleu(pred_str, [target_str])
                    bleu_scores.append(bleu.score)
                for pred_id, target_id in zip(predictions, target_ids):
                    accuracy = SENTIADecoderModel.calculate_accuracy(pred_id, target_id)
                    accuracy_scores.append(accuracy)
                accuracy = sum(accuracy_scores) / len(accuracy_scores)
                bleu = sum(bleu_scores) / len(bleu_scores)
                # Calculate the reward
                reward, penalty = SENTIADecoderModel.get_reward(predictions.tolist()[0], target_ids.tolist()[0])
                ol = loss
                # Backpropagate the loss and update the parameters with the reward
                #if penalty > 0 and penalty > reward:
                    #loss = (loss * ((penalty - reward) * 5))
                #if reward > penalty:
                    #loss = (loss / ((reward - penalty) * 5))
                if torch.isnan(loss):
                    print("Skipped non-finite loss")
                    print(loss.item())
                    continue
                loss.backward()
                torch.nn.utils.clip_grad_value_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                # Update the metrics
                total_loss += loss.item()
                #total_reward += reward
                total_bleu += bleu
                total_perplexity += torch.exp(ol).item()
                num_batches += 1
                wandb.log({"loss": ol.item(), "bleu": bleu, "perplexity": torch.exp(loss).item(), "accuracy": accuracy})
                print(f"Epoch {epoch+1}/{num_epochs}, Batch {i+1}/{len(dataloader)}: Loss - {ol.item():.4f}, NetReward - {reward-penalty:.4f}, BLEU - {bleu:.4f}, Perplexity - {torch.exp(ol).item()}, Accuracy - {accuracy}")
            # Display the metrics for the epoch
            model.save('D:\\Projects\\chatSENTIA\\')
            tokenizer.save_pretrained('D:\\Projects\\chatSENTIA\\')
            val_loss, val_reward, val_penalty, val_bleu, val_perplexity, val_accuracy = SENTIADecoderModel.evaluate(model, val_dataloader, tokenizer, device)
            wandb.log({"val_loss": val_loss.item(), "val_bleu": val_bleu, "val_perplexity": val_perplexity, "val_accuracy": val_accuracy,})
            print(f"Validation metrics: Loss={val_loss:.4f}, Reward={reward-penalty:.4f}, BLEU={val_bleu:.4f}, Perplexity={val_perplexity:.4f}")


    @staticmethod
    def get_reward(predictions, target_ids, bleu_threshold=5):
        """
        Calculate the reward and penalty for the generated predictions.

        Args:
            predictions (list): List of predicted output tokens.
            target_ids (list): List of target output tokens.
            bleu_threshold (float): Threshold for BLEU score reward.
            perplexity_threshold (float): Threshold for perplexity penalty.

        Returns:
            reward (float): Reward score.
            penalty (float): Penalty score.
        """
        reward = 0
        penalty = 0

        # Calculate BLEU score
        # Check each prediction against its corresponding target ID
        for i in range(len(predictions)):
            bleu_score = sentence_bleu([target_ids], predictions)
            # Reward for BLEU score higher than the threshold
            if bleu_score > bleu_threshold:
                reward += 1
            # Penalize for BLEU score lower than 1 by dividing the penalty
            if bleu_score < 1:
                penalty += 1 / (bleu_score + 1)
            if predictions[i] == "[PAD]":
                penalty += 1
            if predictions[i] != "[PAD]":
                reward += 1
            # Penalize for repeating words consecutively
            if i > 0 and predictions[i] == predictions[i - 1]:
                penalty += 1
            # Reward for using words correctly at the same index
            if i < len(target_ids) and predictions[i] == target_ids[i]:
                reward += 1
            elif predictions[i] in target_ids:
                reward += 0.25

        return reward, penalty

    @staticmethod
    def evaluate(model, dataloader, tokenizer, device: torch.device):
        """
        Evaluate the model on the validation set and calculate metrics.

        Args:
            model (nn.Module): Model to evaluate.
            dataloader (DataLoader): Validation data loader.
            tokenizer: Tokenizer for decoding predictions.

        Returns:
            avg_loss (float): Average loss.
            avg_reward (float): Average reward.
            avg_penalty (float): Average penalty.
            avg_bleu (float): Average BLEU score.
            avg_perplexity (float): Average perplexity.
        """
        model.eval()
        total_loss = 0
        total_reward = 0
        total_bleu = 0
        total_perplexity = 0
        num_batches = 0
        total_penalty = 0
        total_accuracy = 0

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                target_ids = batch["labels"].to(device)
                input_ids = input_ids.to(device)
                attention_mask = attention_mask.to(device)
                target_ids = target_ids.to(device)
                target_text = batch["target_text"]
                # Generate the output and calculate the loss
                outputs = model(input_ids=input_ids, labels=target_ids, return_dict=True)
                loss, logits = outputs[:2]
                # Calculate the BLEU score
                predictions = torch.argmax(logits, dim=-1)
                predictions_str = [tokenizer.decode(pred, skip_special_tokens=True) for pred in predictions.tolist()]
                target_str = [tokenizer.decode(tgt, skip_special_tokens=True) for tgt in target_ids.tolist()]
                reward, penalty = SENTIADecoderModel.get_reward(predictions_str[0], target_str[0])
                bleu_scores = []
                accuracy_scores = []
                for pred_str, target_str in zip(predictions_str, target_str):
                    bleu = sacrebleu.sentence_bleu(pred_str, [target_str])
                    bleu_scores.append(bleu.score)
                for pred_id, target_id in zip(predictions, target_ids):
                    accuracy = SENTIADecoderModel.calculate_accuracy(pred_id, target_id)
                    accuracy_scores.append(accuracy)
                accuracy = sum(accuracy_scores) / len(accuracy_scores)
                bleu = sum(bleu_scores) / len(bleu_scores)
                # Update the metrics
                total_loss += loss
                total_reward += reward
                total_penalty += penalty
                total_bleu += bleu
                total_accuracy += accuracy
                total_perplexity += torch.exp(torch.tensor(loss)).item()
                num_batches += 1

        # Calculate the average metrics
        avg_loss = total_loss / num_batches
        avg_reward = total_reward / num_batches
        avg_bleu = total_bleu / num_batches
        avg_perplexity = total_perplexity / num_batches
        avg_penalty = total_penalty / num_batches
        avg_accuracy = total_accuracy / num_batches
        return avg_loss, avg_reward, avg_penalty, avg_bleu, avg_perplexity, avg_accuracy

    def summary(self):
        """
        Print a summary of the model architecture and the number of parameters.
        """
        model = self
        num_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        print("Model Summary:")
        print(f"{'='*40}")
        print(model)
        print(f"{'='*40}")
        print(f"Total params: {num_params}")
        print(f"Trainable params: {trainable_params}")

class MEPA(nn.Module):
    """
    Mutation Enhanced Plasticity Architecture (MEPA) Module with multiple layers.

    This module implements a fully connected layer, also known as a Multi-Layer Perceptron (MLP),
    with an affine transformation. It takes an input tensor and applies a linear transformation
    followed by bias addition. The weights and biases of the module are learned during training.

    Args:
        hidden_dim (int): The size of the input and output features.
        layers (int): The number of layers in the network.
        activation (callable, optional): The activation function to be applied after forwarding
            through all layers. Default is F.sigmoid

    Shape:
        - Input: `(batch_size, hidden_dim)` or `(batch_size, *, hidden_dim)` where `*` represents
          any number of additional dimensions.
        - Output: `(batch_size, hidden_dim)` or `(batch_size, *, hidden_dim)` depending on the
          input shape.

    Example:
        >>> hidden_dim = 10
        >>> batch_size = 32
        >>> input_tensor = torch.randn(batch_size, hidden_dim)
        >>> layers = 3
        >>> mepa = MEPA(hidden_dim, layers)
        >>> output_tensor = mepa(input_tensor)
        >>> print(output_tensor.shape)
        torch.Size([32, 10])
    """

    class MEPALayer(nn.Module):
        """
        A single layer of the Mutation Enhanced Plasticity Architecture (MEPA) module.

        Args:
            hidden_dim (int): The size of the input and output features for this layer.

        Shape:
            - Input: `(batch_size, hidden_dim)`
            - Output: `(batch_size, hidden_dim)`
        """
        def __init__(self, hidden_dim):
            super(MEPA.MEPALayer, self).__init__()
            self.weight = nn.Linear(hidden_dim, hidden_dim)
            self.bias = nn.Parameter(torch.Tensor(hidden_dim))
            self.register_parameter("bias", self.bias)
            self.scaling_matrix = nn.Parameter(torch.randn(hidden_dim) * 0.001)  
            self.register_parameter("scaling_matrix", self.scaling_matrix)
            #self.layer_norm = nn.LayerNorm(hidden_dim)
            #self.rms = nn.LayerNorm(hidden_dim)
            self.ffn = SENTIAFF(hidden_dim)
            self.reset_parameters()

        def reset_parameters(self):
            """
            Initialize the layer's parameters.

            This function initializes the weight, bias, and scaling matrix parameters of the layer
            using Kaiming normal initialization for the weight, and uniform initialization for
            bias and scaling matrix.

            Note:
                Kaiming normal initialization is used for weight initialization, which is suitable
                for activations like sigmoid and tanh.

            Shape:
                - weight: `(hidden_dim, hidden_dim)`
                - bias: `(hidden_dim)`
                - scaling_matrix: `(hidden_dim, hidden_dim)`
            """
            nn.init.xavier_normal_(self.weight.weight)
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)
        def forward(self, x):
            """
            Forward pass of the MEPALayer.

            Args:
                x (torch.Tensor): The input tensor of shape `(batch_size, hidden_dim)`.

            Returns:
                torch.Tensor: The output tensor of shape `(batch_size, hidden_dim)`.
            """
            biased = x + self.bias
            scaled = (biased * self.scaling_matrix) + biased
            ffn_out = self.ffn(scaled) 
            return ffn_out + scaled

    def __init__(self, hidden_dim, layers, activation=None):
        """
        Initialize the Mutation Enhanced Plasticity Architecture (MEPA) module.

        Args:
            hidden_dim (int): The size of the input and output features for each layer.
            layers (int): The number of layers in the network.
            activation (callable, optional): The activation function to be applied after forwarding
                through all layers. Default is F.relu.
        """
        super(MEPA, self).__init__()
        self.activation = None
        self.hidden_dim = hidden_dim
        self.layers = layers
        if activation is not None:
            self.activation = activation()
        self.layer_modules = nn.ModuleList([self.MEPALayer(hidden_dim) for _ in range(layers)])

    def forward(self, x):
        """
        Forward pass of the MEPA module.

        Args:
            x (torch.Tensor): The input tensor of shape `(batch_size, hidden_dim)` or
                `(batch_size, *, hidden_dim)`.

        Returns:
            torch.Tensor: The output tensor of shape `(batch_size, hidden_dim)` or
                `(batch_size, *, hidden_dim)` depending on the input shape.
        """
        if x.dim() > 2:
            x = x.reshape(x.size(0), x.size(1), -1)
        
        for layer_module in self.layer_modules:
            # Apply the current layer's transformation
            x2 = layer_module(x) + x

        # Apply the activation function after forwarding through all layers
        if self.activation is not None:
            x = self.activation(x2)

        return x
class SENTIARotaryEmbedding(nn.Module):
    def __init__(self, in_dim, out_dim, *args, **kwargs):
        super(SENTIARotaryEmbedding, self).__init__(*args, **kwargs)
        self.resize = nn.Linear(in_dim, out_dim)
        self.rot_emb = RotaryEmbedding(dim=out_dim)

    def forward(self, x):
        y = self.resize(x)
        y = self.rot_emb.rotate_queries_or_keys(y)
        return y
class SENTIATransformer(nn.Module):
    """
    Transformer model consisting of an encoder stack and a decoder stack.

    Args:
        config (SENTIAConfig): Configuration for the transformer model.
        num_encoder_blocks (int): Number of encoder blocks in the encoder stack.
        num_decoder_blocks (int): Number of decoder blocks in the decoder stack.

    Shape:
        - Input (encoder): `(batch_size, src_seq_length, hidden_dim)`
        - Input (decoder): `(batch_size, tgt_seq_length, hidden_dim)`
        - Output: `(batch_size, tgt_seq_length, hidden_dim)`
    """

    def __init__(self, config: SENTIAConfig):
        super(SENTIATransformer, self).__init__()
        self.encoder = nn.ModuleList([
            SENTIAEncoderBlock(config) for _ in range(config.n_layer // 2)
        ])
        self.decoder = nn.ModuleList([
            SENTIADecoderBlock(config, True) for _ in range(config.n_layer // 2)
        ])

    def forward(self, tgt_input, tgt_mask=None):
        """
        Forward pass of the transformer model.

        Args:
            src_input (torch.Tensor): The source input tensor.
                Shape: `(batch_size, src_seq_length, hidden_dim)`
            tgt_input (torch.Tensor): The target input tensor.
                Shape: `(batch_size, tgt_seq_length, hidden_dim)`
            src_mask (torch.Tensor): Optional mask tensor for the source input.
                Shape: `(batch_size, src_seq_length, src_seq_length)` (e.g., padding mask).
            tgt_mask (torch.Tensor): Optional mask tensor for the target input.
                Shape: `(batch_size, tgt_seq_length, tgt_seq_length)` (e.g., causal mask).

        Returns:
            torch.Tensor: The output tensor.
                Shape: `(batch_size, tgt_seq_length, hidden_dim)`
        """
        # Encoder stack
        for encoder_block in self.encoder:
            src_input, _ = encoder_block(tgt_input, tgt_mask)

        # Decoder stack
        for decoder_block in self.decoder:
            tgt_input, attn = decoder_block(tgt_input, src_input)

        return tgt_input, attn
class SENTIADecoderTransformer(nn.Module):
    """
    Decoder part of the Transformer with multiple SENTIATransformerBlocks.

    Args:
        hidden_dim (int): The size of the input and output features for each layer.
        num_heads (int): The number of attention heads in each SENTIATransformerBlock.
        num_layers (int): The number of Transformer decoder layers.

    Shape:
        - Input: `(batch_size, seq_length, hidden_dim)`
        - Output: `(batch_size, seq_length, hidden_dim)`
    """

    def __init__(self, config: SENTIAConfig):
        super(SENTIADecoderTransformer, self).__init__()
        self.blocks = nn.ModuleList([
            SENTIADecoderBlock(config)
            for _ in range(config.n_layer)
        ])

    def forward(self, x, mask):
        """
        Forward pass of the SENTIATransformer.

        Args:
            x (torch.Tensor): The input tensor of shape `(batch_size, seq_length, hidden_dim)`.
            mask (torch.Tensor): The attention mask of shape `(batch_size, seq_length, seq_length)`.

        Returns:
            torch.Tensor: The output tensor of shape `(batch_size, seq_length, hidden_dim)`.
        """
        for block in self.blocks:
            x, attn = block(x, mask)
        return x, attn
class SENTIAEncoderBlock(nn.Module):
    """
    Single Transformer Encoder Block with multi-head self-attention and feed-forward layers.

    Args:
        hidden_dim (int): The size of the input and output features for each layer.
        num_heads (int): The number of attention heads in the Transformer block.

    Shape:
        - Input: `(batch_size, seq_length, hidden_dim)`
        - Output: `(batch_size, seq_length, hidden_dim)`
    """

    def __init__(self, config: SENTIAConfig, *args, **kwargs):
        d_model = config.hidden_dim
        d_inner = config.n_inner
        super(SENTIAEncoderBlock, self).__init__(*args, **kwargs)
        self.self_attention = SENTIAAttention(config, "global", False)  # Global self-attention for encoder
        self.ffn = SENTIAFF(d_model, d_inner)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        """
        Forward pass of the encoder block.

        Args:
            x (torch.Tensor): The input tensor.
                Shape: `(batch_size, seq_length, hidden_dim)`
            mask (torch.Tensor): Optional mask tensor for attention.
                Shape: `(batch_size, seq_length, seq_length)` (e.g., padding mask).

        Returns:
            torch.Tensor: The output tensor.
                Shape: `(batch_size, seq_length, hidden_dim)`
        """
        # Multi-head self-attention
        if mask is None:
            mask = SENTIADecoderModel.generate_causal_mask(x)
        attn = self.self_attention(x, mask)[0]
        y = self.norm1(attn + x)  # Residual connection and layer normalization

        # Feed-forward network
        ffn_out = self.ffn(y)
        out = self.norm2(ffn_out + y)  # Residual connection and layer normalization

        return out, attn
class SENTIADecoderBlock(nn.Module):
    """
    Single Transformer Block with masked multi-head, self-attention, and feed-forward layers.

    Args:
        hidden_dim (int): The size of the input and output features for each layer.
        num_heads (int): The number of attention heads in the Transformer block.

    Shape:
        - Input: `(batch_size, seq_length, hidden_dim)`
        - Output: `(batch_size, seq_length, hidden_dim)`
    """

    def __init__(self, config: SENTIAConfig, cross_attention=False, *args, **kwargs):
        d_model = config.hidden_dim
        d_inner = config.n_inner
        super(SENTIADecoderBlock, self).__init__(*args, **kwargs)
        self.masked_attention = SENTIAAttention(config, "local", False)
        self.cross_attention_bool = cross_attention
        if cross_attention:
            self.cross_attention = SENTIAAttention(config, "local", False)
            self.cross_norm = nn.LayerNorm(d_model)
        self.ffn = SENTIAFF(d_model, d_inner)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
    def forward(self, x, encoder_states=None, mask=None, encoder_mask=None):
        
        if mask is None:
            mask = SENTIADecoderModel.generate_causal_mask(x)
        if encoder_mask is None and encoder_states is not None:
            encoder_mask = SENTIADecoderModel.generate_causal_mask(encoder_states)
        attn = self.masked_attention(x, mask)[0]
        y = self.norm1(attn)
        attn1_out = y + x
        if self.cross_attention_bool:
            attn1 = self.cross_attention.forward(attn1_out, encoder_states=encoder_states)[0]
            y = self.cross_norm(attn1)
            attn2_out = attn1_out + y
            y = self.ffn(attn2_out)
            y = self.norm2(y)
            out = y + attn2_out
        else:
            y = self.ffn(attn1_out)
            y = self.norm2(y)
            out = y + attn1_out
        return out, attn
class SENTIADecoderModel(SENTIAPreTrainedModel):
    """
    SENTIA (Self-Enhanced Neural Transformer with Integration and Attention) Model Class.

    This model extends GPT2PreTrainedModel and incorporates Rotary Embeddings and MEPA layers for text generation tasks.

    Args:
        config (SENTIAConfig): Configuration object specifying model parameters.

    Attributes:
        embedding (nn.Embedding): Embedding layer for the input sequence.
        posenc (SENTIARotaryEmbedding): Rotary positional encoding layer.
        mepa (MEPA): MEPA (Mutation Enhanced Plasticity Architecture) layer for dynamic neural connections.
        transformer_decoder (GPT2Model): GPT-2 transformer decoder.
        head_layers (nn.Linear): Fully connected head layers for text generation.
    """

    def __init__(self, config: SENTIAConfig, *args, **kwargs):
        super(SENTIADecoderModel, self).__init__(config, *args, **kwargs)
        self.config = config
        self.embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.rot_emb = SENTIARotaryEmbedding(config.n_embd, config.hidden_dim)
        self.mepa = MEPA(config.hidden_dim, config.n_layer)
        self.transformer_decoder = SENTIADecoderTransformer(config)
        self.drop = nn.Dropout(0.1)
        self.model_parallel = True
        self.register_for_auto_class("AutoModel")
    def get_input_embeddings(self) -> nn.Module:
        return self.embedding
    def _resize_token_embeddings(self, new_num_tokens):
        self.embedding = nn.Embedding(new_num_tokens, self.config.hidden_dim)
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[BaseModelOutput, Dict[str, torch.Tensor]]:
        """
        Forward pass of the SENTIA model.

        Args:
            input_ids (torch.Tensor): Input tensor containing token indices.
            attention_mask (torch.Tensor): Attention mask to indicate padding positions.

        Returns:
            probabilities (torch.Tensor): Predicted probabilities for each token in the vocabulary.
            loss (torch.Tensor or None): Calculated loss if input_ids is provided, otherwise None.
        """
        embd = self.embedding(input_ids)
        embd = self.rot_emb(embd)
        input_ids = None
        embd = self.drop(embd)
        transformer_outputs, attn = self.transformer_decoder(embd, attention_mask)
        mepa_output = self.mepa(attn)
        hidden_states = transformer_outputs + mepa_output
        if return_dict:
            return {
                "last_hidden_state": hidden_states,
            }
        else:
            return BaseModelOutput(
                last_hidden_state=hidden_states,
                attentions=attn
            )
    
class SENTIAModelForCausalLM(SENTIAPreTrainedModel):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config: SENTIAConfig, *args, **kwargs):
        super(SENTIAModelForCausalLM, self).__init__(config, *args, **kwargs)
        self.transformer = SENTIADecoderModel(config, *args, **kwargs)
        self.lm_head = nn.Linear(config.hidden_dim, config.vocab_size, bias=False)
        self.model_parallel = False
        self.register_for_auto_class("AutoModelForCausalLM")   
    def summary(self):
        """
        Print a summary of the model architecture and the number of parameters.
        """
        model = self
        num_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        print("Model Summary:")
        print(f"{'='*40}")
        print(model)
        print(f"{'='*40}")
        print(f"Total params: {num_params}")
        print(f"Trainable params: {trainable_params}") 
    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, inputs_embeds=None, **kwargs):
        token_type_ids = kwargs.get("token_type_ids", None)
        # only last token for inputs_ids if past is defined in kwargs
        if past_key_values:
            input_ids = input_ids[:, -1].unsqueeze(-1)
            if token_type_ids is not None:
                token_type_ids = token_type_ids[:, -1].unsqueeze(-1)
        attention_mask = self.generate_causal_mask(input_ids)
        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                
                "attention_mask": attention_mask,
            }
        )
        return model_inputs
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        return_dict: Optional[bool] = True,
        keytoken_ids: Optional[list] = [],
        output_attentions = None,
        output_hidden_states = None,
    ) -> Union[CausalLMOutput, Dict[str, torch.Tensor]]:
        super_out = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = super_out.last_hidden_state
        lm_logits = self.lm_head(hidden_states)
        #probabilities = F.softmax(lm_logits, dim=-1)
        if labels is not None:
            # move labels to correct device to enable model parallelism
            labels = labels.to(lm_logits.device)
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            batch_size, seq_length, vocab_size = shift_logits.shape
            # Flatten the tokens
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(
                shift_logits.view(batch_size * seq_length, vocab_size), shift_labels.view(batch_size * seq_length)
            )
        else:
            loss = None
        if not return_dict:
            return {
                "loss": loss,
                "logits": lm_logits,
                "attentions": super_out.attentions
                
            }
        else:
            return CausalLMOutput(
                loss=loss,
                logits=lm_logits,
                attentions=super_out.attentions
            )
    def get_input_embeddings(self) -> nn.Module:
        return self.embedding
    def _resize_token_embeddings(self, new_num_tokens):
        self.embedding = nn.Embedding(new_num_tokens, self.config.hidden_dim)
class SENTIAModelForImageGeneration(SENTIAPreTrainedModel):
    """An unconventional way of using transformers for image generation"""
    
    def __init__(self, config: SENTIAConfig, *args, **kwargs):
        super(SENTIAModelForImageGeneration, self).__init__(config, *args, **kwargs)
        self.embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.rot_emb = SENTIARotaryEmbedding(config)
        self.mepa = MEPA(config.hidden_dim, config.n_layer)
        self.drop = nn.Dropout1d(0.1)
        
        # Use SENTIATransformer as the text encoder
        self.transformer = SENTIATransformer(config)
        self.text_encoder = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(config.hidden_dim // 2, config.hidden_dim // 4),
            nn.ReLU(),
            nn.Linear(config.hidden_dim // 4, config.hidden_dim // 8),
            nn.ReLU(),
            nn.Linear(config.hidden_dim // 8, 1),
            nn.Sigmoid()
            )
        self.image_generation_head = nn.Conv2d(1, 1080*1920*3, kernel_size=(5, 1))
        
    def forward(self, text_inputs, labels=None):
        embd = self.embedding(text_inputs)
        embd = self.rot_emb(embd)
        embd = self.drop(embd)
        # Encode text
        y, attn = self.transformer(embd)
        text_embeddings = self.mepa(attn)
        text_embeddings = y + text_embeddings
        # Generate image
        encoded_text = self.text_encoder(text_embeddings)
        image_tensor = self.image_generation_head(encoded_text)
        generated_image = image_tensor.view(1080, 1920, 3)
        loss = None
        if labels is not None:
            loss = F.mse_loss(generated_image, labels)
        return generated_image, loss




