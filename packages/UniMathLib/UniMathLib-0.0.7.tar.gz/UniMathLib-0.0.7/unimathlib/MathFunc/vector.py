

class Vector:
    """Base Vector class.

    A Vector is a one-dimensional mathematical entity that can store a list of numeric values.

    Args:
        arg (int, optional): If an integer, it sets the vector length to 'arg' with zeros. If None, creates a default vector of length 1. Defaults to None.

    Raises:
        ValueError: Raised for unsupported 'arg' types or incorrect string format.

    Methods:
        - __init__(self, arg=None): Create an instance of the Vector class.
        - __str__(self): Return a string representation of the Vector.
        - __len__(self): Return the length of the Vector.
        - __getitem__(self, key): Get an element at the specified index.
        - __setitem__(self, key, value): Set an element at the specified index.
        - __iter__(self): Return an iterator over the elements in the Vector.
        - __add__(self, other): Add two Vectors element-wise or add a scalar to each element.
        - __radd__(self, other): Reverse add function for Vectors and other supported types.
        - __sub__(self, other): Subtract two Vectors element-wise or subtract a scalar from each element.
        - __rsub__(self, other): Reverse subtract function for Vectors and other supported types.
        - __mul__(self, other): Scalar multiplication of Vectors or element-wise multiplication with another Vector.
        - __rmul__(self, other): Reverse multiplication function for Vectors and other supported types.
        - dist(self, y, p=1): Calculate the distance between two Vectors using different p-norms.
        - _euclidean(self, y): Calculate the Euclidean norm between two Vectors.
        - _manhattan(self, y): Calculate the Manhattan norm between two Vectors.
        - _chebyshev(self, y): Calculate the Chebyshev norm between two Vectors.
        - sort(self): Sort the Vector (for 1D numeric Vectors only) using the quicksort algorithm.
        - extend(self, iterable): Extend the Vector by appending elements from the iterable.
        - append(self, item): Append an item to the end of the Vector.
        - clear(self): Remove all elements from the Vector.
        - cross(self, y): Calculate the cross product of two 3D Vectors.
        - size(self): Return the size (dimension) of the Vector.
        - _AllNum(vector): Check if all elements in the Vector are of type int or float.

    Properties:
        - size: Return the size (dimension) of the Vector.

    Example:
        Creating a Vector:
        - v = Vector(5)  # Creates a Vector of length 5 initialized with zeros.
        - v = Vector([1, 2, 3])  # Creates a Vector with the provided list of values.
        - v = Vector("1,2,3,4")  # Creates a Vector from a comma-separated string.
        - v = Vector({"1": [1, 2, 3], "2": [4, 5, 6]})  # Creates a Vector from a dictionary.

        Performing operations:
        - v1 = Vector([1, 2, 3])
        - v2 = Vector([4, 5, 6])
        - v3 = v1 + v2  # Element-wise addition of two Vectors.
        - v4 = v1 - v2  # Element-wise subtraction of two Vectors.
        - v5 = v1 * v2  # Element-wise multiplication of two Vectors.
        - v6 = v1.dist(v2, p=2)  # Calculate the Euclidean distance between two Vectors.

    Supported operations:
    - Vector OP Vector
    - Vector OP scalar
    - List OP Vector
    - Set OP Vector
    - Tuple OP Vector
    - String OP Vector
    - Dictionary OP Vector

    Dist can work with different p-norms (1, 2, or 3).

    """
    def __init__(self,arg=None):
        """
        Create an instance of the Vector class.

        If 'arg' is an integer, it creates a vector of length 'arg' initialized with zeros.
        If 'arg' is None, it creates a default vector of length 1.
        If 'arg' is a supported data type (list, tuple, set, dict, str, Vector), it initializes the vector with the values from 'arg'.
        
        Supported operations with different types of 'arg':
        - List OP Vector
        - Set OP Vector
        - Tuple OP Vector
        - String OP Vector
        - Dictionary OP Vector (keys become the first column and values become the second column)
        - Vector OP Vector (e.g., for distance calculation and cross product)
        
        Examples:
            - arg = [a, b, c]
            vector = [a, b, c]
            - arg = {a, b, c}
            vector = [a, b, c]
            - arg = (a, b, c)
            vector = [a, b, c]
            - arg = {"1": [1, 2, 3], "2": [4, 5, 6]}
            vector = [["1", [1, 2, 3]], ["2", 4, 5, 6]]
            - arg = "1,2,3,4" (string with ',' as separator)
            vector = [1.0, 2.0, 3.0, 4.0]

        Args:
            arg (int, optional): If an integer, it sets the vector length to 'arg' with zeros. If None, creates a default vector of length 1. Defaults to None.

        Raises:
            ValueError: Raised for unsupported 'arg' types or incorrect string format.
        """
        if arg is None:
            arg = 0
        if isinstance(arg, int):
            if arg < 0:
                arg = abs(arg)
            self.dim = arg
            self.vector = [0 for i in range(arg)]
        else:          
            if isinstance(arg,list):
                self.dim = len(arg)
                self.vector = arg
            elif isinstance(arg,tuple):
                self.dim = len(arg)
                self.vector = list(arg)
            elif isinstance(arg,set):
                self.dim = len(arg)
                self.vector = list(arg)
            elif isinstance(arg,dict):
                self.dim = len(arg.keys())
                self.vector = [[k,v] for k,v in arg.items()]
            elif isinstance(arg, str):
                try:
                    str_vec = list(map(float, arg.split(",")))
                except: raise ValueError(f"Incorrect string type | example 'a,b,c,d' where a,b,c,d is numbers | your str -> {arg}")
                self.dim = len(str_vec)
                self.vector = str_vec
            elif isinstance(arg, str):
                self.dim = len(arg)
                self.vector = arg
            elif isinstance(arg, Vector):
                self.dim = len(arg)
                self.vector = [i for i in arg]
            else:
                raise ValueError(f"For arg can be used only (list, tuple, set, dict, str, int, Vector) objects | your arg:{arg}; type:{type(arg)}")

    
    def __iter__(self):
        """Return an iterator over the elements in the vector.

        Returns:
            iterator: An iterator over the elements in the vector.
        """
        return iter(self.vector)
                    
    
    def __len__(self):
        """Get the number of elements in the vector.

        Returns:
            int: The number of elements in the vector.
        """
        return self.dim


    def __mul__(self, other):
        """Perform scalar multiplication of vectors or vector-scalar multiplication.

        Args:
            other (Vector, int, float): The second vector or scalar.

        Raises:
            ValueError: If the format of the 'other' argument is invalid.

        Returns:
            Union[Scalar, Vector]: The result of scalar multiplication or vector-scalar multiplication.
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
        if isinstance(other, (Vector,int,float)):
            if isinstance(other,Vector):
                if self.dim == other.dim and other._AllNum() and self._AllNum():
                    return sum(a*b for a,b in zip(self.vector,other.vector))
            else:  
                return Vector([a*other for a in self.vector])
        else:
                raise ValueError(f"Error in other format, please check {other}")
        
    def __rmul__(self, other):
        """Perform scalar multiplication with the vector on the right-hand side.

        Args:
            other (Vector, int, float): The second vector or scalar.

        Raises:
            ValueError: If the format of the 'other' argument is invalid.

        Returns:
            Union[Scalar, Vector]: The result of scalar multiplication or vector-scalar multiplication.
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
            if self.dim == other.dim and other._AllNum() and self._AllNum():
                return sum(a*b for a,b in zip(self.vector,other.vector))
            else:
                raise ValueError(f"Error in other format, please check {other}")
        if isinstance(other, (int,float)):
            return Vector([a*other for a in self.vector])
        else:
            raise ValueError(f"Error in other.vector format, please check {other}")
    def __str__(self):
        """Get a string representation of the vector.

        Returns:
            str: A string representation of the vector.
        """

        return str(self.vector)

    def __setitem__(self, key, value):
        """Set an element or slice of elements in the vector.

        Args:
            key: An index or slice to set in the vector.
            value: The value to set at the specified index or slice.
        """

        self.vector[key] = value
        
    def __radd__(self, other):
        """Perform addition of vectors or vector-list addition.

        Args:
            other (list, tuple, set, dict, str): The other vector or iterable.

        Raises:
            ValueError: If the format of the 'other' argument is invalid.

        Returns:
            Vector: The result of vector addition.
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
            if self.dim == other.dim and other._AllNum() and self._AllNum():
                return Vector([a+b for a,b in zip(self.vector,other.vector)])
            else:
                raise ValueError(f"Error in other format, please check {other}")
        else:
                raise ValueError(f"Error in other.vector format, please check {other}")

    def __rsub__(self, other):
        """Subtract the vector from another vector or an iterable (list, tuple, set, dict, str).

        Args:
            other (list, tuple, set, dict, str, Vector): The other vector or iterable.

        Raises:
            ValueError: If the format of `other` is invalid.

        Returns:
            Vector: The result of the subtraction (self - other).
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
            if self.dim == other.dim and other._AllNum() and self._AllNum():
                return Vector([a-b for a,b in zip(self.vector,other.vector)])
            else:
                raise ValueError(f"Error in other format, please check {other}")
        else:
                raise ValueError(f"Error in other.vector format, please check {other}")

    def __add__(self, other):
        """Add the vector to another vector or an iterable (list, tuple, set, dict, str).

        Args:
            other (list, tuple, set, dict, str, Vector): The other vector or iterable.

        Raises:
            ValueError: If the format of `other` is invalid.

        Returns:
            Vector: The result of the addition (self + other).
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
        if isinstance(other, Vector):
            if self.dim == other.dim and other._AllNum() and self._AllNum():
                return Vector([a+b for a,b in zip(self.vector,other.vector)])
            else:
                raise ValueError(f"Error in other.vector format, please check {other}")
        else:
                raise ValueError(f"Error in other.vector format, please check {other}")
    
    def __getitem__(self, key):
        """Get an element or slice from the vector.

        Args:
            key: An index or slice to retrieve from the vector.

        Returns:
            Any: The element or slice of elements from the vector.
        """
        return self.vector[key]

    def __sub__(self, other):
        """Subtract another vector or an iterable (list, tuple, set, dict, str) from the vector.

        Args:
            other (list, tuple, set, dict, str, Vector): The other vector or iterable.

        Raises:
            ValueError: If the format of `other` is invalid.

        Returns:
            Vector: The result of the subtraction (self - other).
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
        if isinstance(other, Vector):
            if self.dim == other.dim and other._AllNum() and self._AllNum():
                return Vector([a-b for a,b in zip(self.vector,other.vector)])
            else:
                raise ValueError(f"Error in other.vector format, please check {other}")
        else:
                raise ValueError(f"Error in other.vector format, please check {other}")
    
    
    @property
    def sort(self):
        """Sort the vector in ascending order.

        Note:
            This method is only for 1D vectors containing numeric elements.

        Raises:
            ValueError: If the vector format is not valid or if it's empty.

        Returns:
            Vector: The sorted vector.
        """
        if self._AllNum()  or len(self)==0:
            if len(self) <= 1:
                return self

            stack = [(0, len(self) - 1)]  # Используем стек для хранения индексов начала и конца подмассивов

            while stack:
                left, right = stack.pop()
                pivot_index = self._partition(left, right)

                if pivot_index - 1 > left:
                    stack.append((left, pivot_index - 1))
                if pivot_index + 1 < right:
                    stack.append((pivot_index + 1, right))

            return self
        else:
                raise TypeError(f"Error in self.vector format, please check {self}")
        
    
    def _partition(self, left, right):
        """Partition the vector into two subvectors around a pivot element.

        This method is used internally by the quicksort algorithm.

        Args:
            left (int): The left index of the subvector.
            right (int): The right index of the subvector.

        Returns:
            int: The index of the pivot element after partitioning.
        """
        pivot = self[right]
        i = left - 1

        for j in range(left, right):
            if self[j] <= pivot:
                i += 1
                self[i], self[j] = self[j], self[i]

        self[i + 1], self[right] = self[right], self[i + 1]
        return i + 1
    

    @property
    def size(self):
        """Get the size (dimension) of the vector.

        Returns:
            int: The dimension of the vector.
        """
        return self.dim
    def extend(self, iterable):
        """Extend the vector by appending elements from an iterable.

        Args:
            iterable: An iterable containing elements to append to the vector.
        """
        self.vector.extend(iterable)
        self.dim += len(iterable)
    
    def append(self, item):
        """Append an item to the end of the vector.

        Args:
            item: The item to append.
        """
        self.vector.append(item)
        self.dim += 1

    def clear(self):
        """
        Remove all elements from the vector.
        """
        self.vector.clear()
        self.dim = 0


    
    def cross(self,y):
        """Calculate the cross product of two 3-dimensional vectors.

        Args:
            y (list, tuple, set, dict, str, Vector): The second vector.

        Raises:
            ValueError: If either vector is not 3-dimensional.

        Returns:
            Vector: The cross product vector.
        """
        if isinstance(other, (list, tuple, set, dict, str)):
            other = Vector(other)
        if isinstance(other, Vector):
            if len(self) != 3 or len(y) != 3:
                raise ValueError("Vector must be 3 dimensional")
            result = Vector([
            self[1] * y[2] - self[2] * y[1],
            self[2] * y[0] - self[0] * y[2],
            self[0] * y[1] - self[1] * y[0]
            ])
            return result
        
    def dist(self,y,p = 1):
        """Calculate the distance between two vectors.

        Args:
            y (list, tuple, set, dict, str, Vector): The second vector.
            p (int, optional): The norm to use for distance calculation (1, 2, or 3). Defaults to 1.

        Raises:
            ValueError: If 'y' is of an incorrect format or 'p' is not 1, 2, or 3.

        Returns:
            scalar: The calculated distance between the vectors.
        """
        if isinstance(y, (list, tuple, set, dict, str)):
            y = Vector(y)
        if isinstance(self,(Vector)) and  isinstance(y,(Vector)) and self._AllNum() and y._AllNum():
            if p == 1:
                return self._euclidean(y)
            elif p == 2:
                return self._manhattan(y)
            elif p == 3:
                return self._chebyshev(y)
            else:
                raise ValueError(f"p can be 1, 2 or 3 | your p = {p}")
        else:
            raise ValueError(f"Error in vector format, please check {(self,y)}")
    
    def _euclidean(self, y):
        """Calculate the Euclidean norm of two vectors.

        Args:
            y (Vector): The second vector.

        Returns:
            scalar: The Euclidean norm between the vectors.
        """
        return sum(abs(x-y)**2 for x,y in zip(self.vector,y.vector))**(1/2)
      
    def _manhattan(self, y):
        """Calculate the Manhattan norm of two vectors.

        Args:
            y (Vector): The second vector.

        Returns:
            scalar: The Manhattan norm between the vectors.
        """
        return sum(abs(x-y) for x,y in zip(self.vector,y.vector))
    
    def _chebyshev(self, y):
        """Calculate the Chebyshev norm of two vectors.

        Args:
            y (Vector): The second vector.

        Returns:
            scalar: The Chebyshev norm between the vectors.
        """
        return max([abs(x-y) for x,y in zip(self.vector,y.vector)])


    def _AllNum(vector):
        """Checks if all elements in a Vector are numbers (int or float).

        Args:
            vector (Vector): The Vector to check.

        Raises:
            TypeError: If the vector has an incorrect type.

        Returns:
            bool: True if all elements in the Vector are numbers (int or float), False otherwise.
        """
        if isinstance(vector, Vector):
            for element in vector:
                if not isinstance(element, (int, float)):
                        return False
                return True
        else:
            raise TypeError(f"_AllNum(vector:Vector) | Your _AllNum(vector:{type(vector)})")