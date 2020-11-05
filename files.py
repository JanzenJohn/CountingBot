import pickle


def read(file):
    f = open(file, "rb")
    output = pickle.load(f)
    f.close()
    return output



def write(file, data):
    with open(file, "wb")as f:
        pickle.dump(data, f)
        f.close()
