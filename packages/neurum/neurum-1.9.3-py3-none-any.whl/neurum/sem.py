from txtai.embeddings import Embeddings
embeddings=Embeddings()
data = ["hydrogen has 1 electron", "python is the best language"]
while True:
        query=input("prompt: ")
        uid=embeddings.similarity(query=query, data=data)[0][0]
        res=data[uid]
        print(res)
        print("-" * 50)