class DatasetConfig:
    def __init__(self, config: dict):
        self.output_dir = config['dataset']['output_dir']
        self.origin_config = config
