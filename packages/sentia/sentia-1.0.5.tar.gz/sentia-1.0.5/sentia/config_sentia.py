from transformers import GPTNeoConfig


class SENTIAConfig(GPTNeoConfig):

    def __init__(
        self, 
        vocab_size=50261,
        hidden_dim=1024,
        n_embed=1024,
        n_layer=12,
        n_head=16,
        n_inner=2048,
        pdrop = 0.0,
        cross_attention=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.hidden_size = hidden_dim
        self.n_embd = n_embed
        self.n_layer = n_layer
        self.num_hidden_layers = n_layer
        self.n_head = n_head
        self.bad_words_ids = None
        self.n_inner = n_inner
        self.pdrop = pdrop
        self.add_cross_attention = True