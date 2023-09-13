class Node:
    def __str__(Self):
        Representation = (f"Node Object: {Self.__repr__()}\n"+
                          f"Node Value: {Self.Value}\n"+
                          f"Next Node Object: {Self.Next.__repr__()}\n")
        if Self.IsHead:
            Representation = f"Node Is A Head\n" + Representation

        return Representation