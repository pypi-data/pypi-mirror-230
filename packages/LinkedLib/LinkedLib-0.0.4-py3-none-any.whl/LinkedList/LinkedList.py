from .ListNode import ListNode

class LinkedList:
    def __init__(Self):
        Self.Head: ListNode = ListNode()
        Self.Head.IsHead = True
        Self.Tail: ListNode = None
        Self.Cursor: ListNode = None


    def Populate_List(Self, List: list):
        Temp = Self.Head
        ListLength = len(List) - 1
        for Index, Datum in enumerate(List):
            Temp.Value = Datum
            if Index == ListLength:
                break
            Temp.Next = ListNode()
            Temp = Temp.Next
        Self.Tail = Temp


    def Get_Content(Self, Index):
        return Self.Traverse(Index).Value


    def Traverse(Self, Index):
        Temp = Self.Head
        Counter = 0
        while True:
            Counter += 1
            if Counter == Index:
                Self.Cursor = Temp
                return Temp
            if Temp.Next == None:
                raise IndexError(f"Index exceeded amount of items. There are only {Counter} items in this list.")
            Temp = Temp.Next
            

    def Insert_At(Self, Index, Value):
        Temp = Self.Traverse(Index)
        List = [Temp.Value]
        Temp.Value = Value
        List += Self.Get_List(Index+1)
        Self.Append(List)


    def Append(Self, List:list):
        Temp = Self.Tail
        ListLength = len(List) - 1
        for Index, Datum in enumerate(List):
            Temp.Value = Datum
            if Index == ListLength:
                break
            Temp.Next = ListNode()
            Temp = Temp.Next


    def Get_List(Self, Index=None):
        List = []
        Temp = Self.Head
        if Index == None:
            while True:
                List.append(Temp.Value)
                if Temp.Next == None:
                    return List
                Temp = Temp.Next
        else:
            Counter = 0
            while True:
                Counter += 1
                if Counter >= Index:
                    List.append(Temp.Value)
                if Temp.Next == None:
                    return List
                Temp = Temp.Next

    
    def Print_Chain(Self):
        Temp = Self.Head
        while True:
            print(str(Temp))
            if Temp.Next == None:
                break
            Temp = Temp.Next


    def Print_Contents(Self):
        Temp = Self.Head
        while True:
            print(Temp.Value)
            if Temp.Next == None:
                break
            Temp = Temp.Next