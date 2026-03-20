from rag import ask_rag

while True:
    q = input("\nAsk a question (or type quit): ")
    if q.lower() == "quit":
        break

    result = ask_rag(q)
    print("\nANSWER:\n")
    print(result["answer"])
    print("\nSOURCES:\n")
    for s in result["sources"]:
        print(s)
