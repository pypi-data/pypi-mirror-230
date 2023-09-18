# def generate_embeddings(
#     self,
#     model_name: str,
#     tokenizer_name: str,
#     model_class: str = "AutoModel",
#     tokenizer_class: str = "AutoTokenizer",
#     batch_size: int = 32,
# ):
#     """
#     Generate embeddings for a given dataset and save them in the output folder.

#     Args:
#         model_name (str): The name or path of the pre-trained model.
#         tokenizer_name (str): The name or path of the tokenizer.
#         model_class (str, optional): The class name for the model. Defaults to "AutoModel".
#         tokenizer_class (str, optional): The class name for the tokenizer. Defaults to "AutoTokenizer".
#         dataset_path (str): The path to the dataset file.
#         output_file_name (str, optional): The name of the output file where embeddings will be saved. Defaults to "embeddings.pt".
#         batch_size (int, optional): The batch size for processing. Defaults to 32.
#     """
#     self.model_name = model_name
#     self.tokenizer_name = tokenizer_name
#     self.model_class = model_class
#     self.tokenizer_class = tokenizer_class

#     # Load dataset
#     self.preprocess_data()

#     # Load model and tokenizer
#     self.load_models()

#     # Initialize DataLoader
#     dataloader = DataLoader(self.train_dataset, batch_size=batch_size)
#     self.model.eval()

#     with torch.no_grad():
#         for batch in dataloader:
#             if isinstance(batch, BatchEncoding):
#                 inputs = batch
#             else:
#                 inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True)

#             outputs = self.model(**inputs)

#             embeddings = torch.cat(outputs.last_hidden_state, dim=0)
#             torch.save(embeddings, os.path.join(self.output.get(), f"embeddings-{str(shortuuid.uuid())}.pt"))
