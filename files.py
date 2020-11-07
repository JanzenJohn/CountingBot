import pickle


def read(file):
    f = open(file, "rb")
    output = pickle.load(f)
    f.close()
    return output



def write(file, data):
    f = open(file, "wb")
    pickle.dump(data, f)
    f.close()

