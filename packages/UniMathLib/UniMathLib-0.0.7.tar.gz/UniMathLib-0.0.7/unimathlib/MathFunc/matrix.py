from .vector import Vector
import copy
import random
import warnings

class Matrix():
    """
    Base Matrix class for performing matrix operations.
    
    This class provides a set of methods and functionalities for working with matrices, including basic matrix
    operations, solving linear systems, finding determinants, and more.

    Methods:
        __init__(*args): 
            Initialize a matrix. Accepts various formats, including dimensions (rows, cols), 
            a list of lists, or a Vector object.

        __str__():
            Return a string representation of the Matrix.

        __iter__():
            Return an iterator for the Matrix.

        __len__():
            Return the number of rows in the Matrix.

        __getitem__(key):
            Get a specific element or row of the Matrix using indexing.

        __setitem__(key, value):
            Set a specific element or row of the Matrix using indexing.

        __eq__(other):
            Compare two matrices for equality.

        __ne__(other):
            Compare two matrices for inequality.

        __mul__(other):
            Multiply the Matrix by another Matrix(Vector) or a scalar.

        __rmul__(other):
            Multiply a scalar by the Matrix.

        __sub__(other):
            Subtract another Matrix from the current Matrix.

        __add__(other):
            Add another Matrix to the current Matrix.

        __invert__(dig=5):
            Find the inverse of a square matrix.

        identity(N):
            Static method to create an NxN identity matrix.

        diag(k, N, M):
            Static method to create a diagonal matrix with a specified value on the diagonal.

        transpose():
            Transpose the current Matrix.

        shape:
            Property to get the shape (rows, cols) of the Matrix.

        determinant(dig=5):
            Calculate the determinant of the Matrix.

        QR():
            Perform QR decomposition of the Matrix.

        LU():
            Perform LU decomposition of the Matrix.
            
        LU_solver(A, b):
            Solve a linear system Ax = b using LU decomposition.

        jacobi_solver(A, b, max_iterations=1000, tolerance=1e-6, check=True):
            Solve a linear system Ax = b using the Jacobi method.

        gauss_solver(A, b):
            Solve a linear system Ax = b using the Gauss elimination method.
        
        SVD(max_iterations: int = 100, tolerance: float = 1e-10):
            Compute the Singular Value Decomposition (SVD) of the matrix using the QR algorithm.
        
        QR_eigen(max_iterations: int = 100):
            Compute eigenvalues and eigenvectors using QR algorithm
   
    
    Attributes:
        rows (int):
            The number of rows in the Matrix.

        cols (int):
            The number of columns in the Matrix.

        matrix (Vector):
            A Vector object representing the matrix data.
    """
    def __init__(self,*args):
        """
        Initialize a Matrix object.

        Args:
            *args: Variable-length arguments that define the matrix.
                The matrix can be defined in one of the following ways:
                - (int, int): Define the matrix dimensions (rows, cols).
                - (list): Define the matrix using a list of lists.
                - (Vector): Define the matrix using a vector.

        Raises:
            ValueError: If the input arguments are invalid or the matrix shape is incorrect.
            IndexError: If there are issues with the provided data during matrix construction.
        """
        if len(args)<1:
            raise ValueError("invalid *args")
        if len(args) == 1 and isinstance(args[0],int):
            self.rows = args[0]
            self.cols = args[0]
            self.matrix = Vector([Vector(args[0]) for i in range(args[0])])
        if len(args) >= 2 and isinstance(args[0],int) and isinstance(args[1],int):
            self.rows = args[0]
            self.cols = args[1]
            self.matrix = Vector([Vector(args[1]) for i in range(args[0])])
        if len(args) >= 1 and isinstance(args[0],(list)):
            rows = len(args[0])
            check = isinstance(args[0][0], (int,float))
            for i in args[0]:
                if isinstance(i, (int,float)) != check:
                    raise IndexError(f"Incorrect construction of of Matrix | el {i}")
            if isinstance(args[0][0], (int,float)):
                self.rows = 1
                self.cols = len(args[0])
                self.matrix = Vector(args[0])
                return
            else: 
                try:
                    cols = len(args[0][0]); 
                    for row in args[0]:
                        if cols != len(row):
                            raise IndexError(f"Incorrect shape of Matrix -> in line {row} is {len(row)} elements")
                finally:pass
            self.rows = rows
            self.cols = cols
            self.matrix =  Vector([Vector(row) for row in args[0]])     
        if len(args) >= 1 and isinstance(args[0],(Vector)):
            rows = len(args[0])
            check = isinstance(args[0][0], (int,float))
            for i in args[0]:
                if isinstance(i, (int,float)) != check:
                    raise IndexError(f"Incorrect construction of of Matrix | el {i}")
            if isinstance(args[0][0], (int,float)):
                self.rows = 1
                self.cols = len(args[0])
                self.matrix = Vector([arg for arg in args[0]])
                return
            else: 
                try:
                    cols = len(args[0][0]); 
                    for row in args[0]:
                        if cols != len(row):
                            raise IndexError(f"Incorrect shape of Matrix -> in line {row} is {len(row)} elements")
                finally:pass     
            self.rows = rows
            self.cols = cols
            self.matrix = Vector([Vector(row) for row in args[0]])

    def __str__(self):
        """
        Return a string representation of the Matrix.

        Returns:
            str: The string representation of the matrix.
        """
        
        if self.rows == 1:
            send=''
            for row in self.matrix:
                send += str(row)+', '
            return '\n'+send[:len(send)-2]
        else:
            return '\n'.join([', '.join(map(str, row)) for row in self.matrix])+'\n'
    
    def __iter__(self):
        """
        Return an iterator over the elements of the matrix.

        Returns:
            iterator: An iterator over the elements.
        """
        return iter(self.matrix)
    
    def __setitem__(self, key, value):
        """
        Set elements or slices in the matrix.

        Args:
            key (int, slice, tuple): The index or slice to set.
            value (element, list, or Matrix): The value to set at the specified index or slice.
        
        Raises:
            IndexError: If the index or slice is invalid or out of bounds.
            ValueError: If the provided value is not compatible with the matrix shape.
        """
        if type(key) != int:
            if key.__class__ != slice:
                try: 
                    row, col = key
                except:
                        raise IndexError(f"Invalide indexation | {key}") 
                        return
                if 0 <= row < self.rows and 0 <= col < self.cols:
                        if self.rows == 1:
                            self.matrix[0][col] = value
                        else:
                            self.matrix[row][col] = value
                else:
                        raise IndexError(f"Out of index | (0 <= row <= {self.rows-1}, 0 <= col <= {self.cols-1}   | your index [{row}][{col}]") 
            else: value = Vector(value); self.matrix[key] = value
        else:
            row = key
            if isinstance(value,(list, tuple, set, dict, str)):
                value = Vector(value)
            elif isinstance(value, Vector):
                pass
            else:
                raise ValueError(f"For value can be used only (list, tuple, set, dict, str, int, Vector) objects | your value:{value}; type:{type(value)}") 
            cols = len(value)
            if 0 <= row < self.rows and cols == self.cols:
                self.matrix[row] = value
            else:
                raise ValueError(f"Out of index | len(value) may be equal to self.rows | get value len = {cols} and self.cols = {self.cols}") 
    
    
    def __getitem__(self, key):
        """
        Get elements or slices from the matrix.

        Args:
            key (int, slice, tuple): The index or slice to access.

        Returns:
            element, list, or Matrix: The accessed element, list of rows, or a submatrix.
        
        Raises:
            IndexError: If the index or slice is invalid or out of bounds.
        """
        if type(key) != int:
                if key.__class__ != slice:
                    try: 
                            row, col = key
                    except:
                            raise IndexError(f"Invalide indexation | {key}") 
                            return
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        if self.rows == 1:
                            return self.matrix[0][col]
                        else:
                            return self.matrix[row][col]
                    else:
                        raise IndexError(f"Out of index | (0 <= row <= {self.rows-1}, 0 <= col <= {self.cols-1}   | your index [{row}][{col}]") 
                else: return self.matrix[key]
        else:
            row = key
            if 0 <= row < self.rows:
                if self.rows == 1:
                    return self.matrix
                return self.matrix[row]
            else:
                raise IndexError(f"Out of index | max index [{self.rows-1}] | your index [{row}]") 
    
    
    def __add__(self, other):
        """
        Add another matrix to this matrix.

        Args:
            other (Matrix): The second matrix to add.

        Raises:
            ValueError: Operator + can be used only for matrices with the same shape.

        Returns:
            Matrix: The result matrix after addition.
        """
        if isinstance(other, Matrix) and self.shape == other.shape:
            result = Matrix(self.rows, self.cols)
            for i,row1,row2 in zip(range(self.rows),self,other):
                result[i] = row1+row2
            return result
        else:
            raise ValueError(f"Operator + can be used only for Matrix With Same shape | Your Matrix Shapes : Matrix1: {self.rows,self.cols}, Matrix2: {other.rows,other.cols} ")
        

    def __sub__(self, other):
        """
        Subtract another matrix from this matrix.

        Args:
            other (Matrix): The second matrix to subtract.

        Raises:
            ValueError: Operator - can be used only for matrices with the same shape.

        Returns:
            Matrix: The result matrix after subtraction.
        """
        if isinstance(other, Matrix) and self.shape == other.shape:
            result = Matrix(self.rows, self.cols)
            for i,row1,row2 in zip(range(self.rows),self,other):
                result[i] = row1-row2
            return result
        else:
            raise ValueError(f"Operator - can be used only for Matrix With Same shape | Your Matrix Shapes : Matrix1: {self.rows,self.cols}, Matrix2: {other.rows,other.cols} ")
        
    def __rmul__(self, other):
        """
        Multiply a scalar, matrix, or vector from the left side of the matrix.

        Args:
            other (int, float, Matrix): The scalar, matrix, or vector to multiply from the left.

        Raises:
            TypeError: Operator * can be used only for Matrix or scalar.

        Returns:
            Matrix: The result of the multiplication.
        """
        if isinstance(other, (Vector,list)):
            return Matrix(other)*self
        if isinstance(other, (int, float)):
            result = Matrix(self.rows, self.cols)
            for i,row1 in zip(range(self.rows),self):
                result[i] = other*row1
            return result
        else:
            raise TypeError("Operator * can be used only for Matrix or scalar")
    
    def __invert__(self, dig:int=5):
        """
        Find the inverse of a matrix.

        Args:
            dig (int): The number of digits to round the result to. Defaults to 5| Change in this function :).

        Raises:
            ValueError: If the matrix is not square (NxN).
            ValueError: If the determinant of the matrix is zero.

        Returns:
            Matrix: The inverted matrix.
        """
        if self.rows != self.cols:
            raise ValueError("Matrix shape may be (N,N)")
        if self.determinant() == 0:
            raise ValueError("Determinantt of Matrix is 0")
        
        n = len(self)
        AM = copy.deepcopy(self)
        IM = Matrix.identity(self.rows)

    
        # Section 3: Perform row operations
        indices = list(range(n)) # to allow flexible row referencing ***
        for fd in range(n): # fd stands for focus diagonal
            fdScaler = round(1.0 / AM[fd][fd], dig)
            # FIRST: scale fd row with fd inverse. 
            for j in range(n): # Use j to indicate column looping.
                AM[fd][j] = round(AM[fd][j]*fdScaler, dig)
                IM[fd][j] = round(IM[fd][j]*fdScaler, dig)
            # SECOND: operate on all rows except fd row as follows:
            for i in indices[0:fd] + indices[fd+1:]: 
                # *** skip row with fd in it.
                crScaler = AM[i][fd] # cr stands for "current row".
                for j in range(n): 
                    # cr - crScaler * fdRow, but one element at a time.
                    AM[i][j] = round(AM[i][j] - crScaler * AM[fd][j], dig)
                    IM[i][j] = round(IM[i][j] - crScaler * IM[fd][j], dig)
        return IM
    
    def __mul__(self, other):
        """
        Multiply the matrix by another matrix or a scalar.

        Args:
            other (Vector, Matrix, int, float): The matrix or scalar to multiply with.

        Raises:
            ValueError: If the number of columns in the first matrix is not equal to the number of rows in the second matrix.
            TypeError: If the type of the 'other' object is not int, float, or Matrix.

        Returns:
            Matrix: The result matrix after multiplication.
        """

        if isinstance(other, (Vector,list)):
            other = Matrix(other) 
        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(f"First Matrix cols must be equal second Matrix rows | your Matrix1_cols: {self.cols}, Matrix2_rows: {other.rows}")
            result = Matrix(self.rows, other.cols)
            for i,row in zip(range(self.rows),self):
                col = []
                for l in range(other.cols):
                    col = []
                    for k in range(self.cols):

                        col.append(other[k][l])
                    result[i][l] = row*Vector(col)
            return result

        elif isinstance(other, (int, float)):
            result = Matrix(self.rows, self.cols)
            for i,row1 in zip(range(self.rows),self):
                result[i] = other*row1
            return result
        
        else:
            raise TypeError("Operator * can be used only for Matrix or scalar")
    
    
    def __ne__(self, other):
        """
        Compare two matrices for inequality.

        Args:
            other (Matrix): The other matrix to compare.

        Returns:
            bool: False if self is equal to other, True if self is not equal to other.
        """
        if self.shape != other.shape:
            return False
        for row1, row2 in zip(self,other):
            for el1, el2 in zip(row1,row2):
                if el1 == el2:
                    return False
        return True
    
    def __eq__(self, other):
        """
        Compare two matrices for equality.

        Args:
            other (Matrix): The other matrix to compare.

        Returns:
            bool: True if self is equal to other, False otherwise.
        """
        if self.shape != other.shape:
            return False
        for row1, row2 in zip(self,other):
            for el1, el2 in zip(row1,row2):
                if el1 != el2:
                    return False
        return True
    
    def __len__(self):
        """
        Get the number of rows in the matrix.

        Returns:
            int: The number of rows in the matrix.
        """
        return self.rows
    
    
    def transpose(self):
        """
        Transpose the matrix.

        Returns:
            Matrix: The transposed matrix.
        """
        return Matrix([[self[j][i] for j in range(self.rows)] for i in range(self.cols)])
    
    @property
    def shape(self):
        """
        Get the shape (number of rows and columns) of the matrix.

        Returns:
            tuple: A tuple containing the number of rows and columns in the matrix.
        """
        return (self.rows,self.cols)
    

    @staticmethod
    def diag(k, N:int, M:int):
        """
        Create a diagonal NxM matrix with the value 'k' on the diagonal.

        Args:
            k (): The value to be placed on the diagonal.
            N (int): The number of rows in the matrix.
            M (int): The number of columns in the matrix.

        Returns:
            Matrix: The NxM diagonal matrix with 'k' on the diagonal.
        """
        matrix = Matrix(N, M)
        if isinstance(k,(Vector,list,set,tuple)):
            for i,k in zip(range(min(N,M)),k):
                matrix[i][i] = k
            return matrix
        for i in range(min(N,M)):
            matrix[i][i] = k
        return matrix
    
    @staticmethod
    def identity(N:int):
        """
        Create an NxN identity matrix.

        Args:
            N (int): The size of the identity matrix (NxN).

        Returns:
            Matrix: The NxN identity matrix.
        """
        return Matrix.diag(1,N,N)
    

    def determinant(self, dig:int=5):
        """
        Calculate the determinant of the matrix.

        Args:
            dig (int): The number of decimal places for the result. Defaults to 5.

        Returns:
            float: The determinant value of the matrix.
        """
        if self.rows == self.cols:
            if self.rows == 1:
                return self[0][0]
            # Прямой ход (преобразование в верхнетреугольную форму)
            det = 1
            mat_copy = copy.deepcopy(self)
            for i in range(self.rows):
                # Если на диагонали встречается ноль, меняем строки местами
                if mat_copy[i][i] == 0:
                    for j in range(i + 1, self.rows):
                        if mat_copy[j][i] != 0:
                            mat_copy[i], mat_copy[j] = mat_copy[j], mat_copy[i]
                            det *= -1  # Изменение знака при перестановке строк
                            break
                # Если на диагонали остался ноль, то детерминант равен нулю
                if mat_copy[i][i] == 0:
                    return 0 
                # Делим текущую строку на диагональный элемент
                pivot = mat_copy[i][i]
                det *= pivot
                for j in range(i, self.rows):
                    mat_copy[i][j] /= pivot
                # Вычитаем текущую строку из остальных строк для обнуления под диагональю
                for j in range(i + 1, self.rows):
                    factor = mat_copy[j][i]
                    for k in range(i, self.rows):
                        mat_copy[j][k] -= factor * mat_copy[i][k]
            for i in range(self.rows):
                det *= mat_copy[i][i]
                return round(det,dig)
        
        else:
            raise ValueError(f"Matrix should be NxN | your matrix shape {self.rows,self.cols}")
    

    def gauss_solver(A, b):
        """
        Solve the linear system Ax = b using the Gauss method.

        Args:
            A (Matrix, list): The matrix A for Ax = b. It must be an NxN matrix.
            b (Matrix, list): The right-hand side vector or matrix b. If b is a list, it should be in the format [[b1], [b2], ...].
                If b is a Matrix, it should have dimensions (n, 1).

        Raises:
            ValueError: If A is not an NxN matrix.
            ValueError: If the determinant of A is zero or if A has infinite solutions.
            ValueError: If the shape of b is incorrect.
            TypeError: If A or b are not of type list, Matrix, or Vector.

        Returns:
            Matrix: The result matrix x, representing the solution to the linear system Ax = b.
        """
     
        if isinstance(A, (list,Matrix, Vector)) and isinstance(b, (list,Matrix,Vector)):
            if isinstance(A,(list, Vector)):
                if len(A) != len(A[0]):
                    raise ValueError("A must be NxN Matrix")
                else:
                    A = Matrix(A)
            if A.determinant() == 0:
                raise ValueError("Matrix determinant = 0 | inf asnwers") 
            if isinstance(b,(list,Vector)):
                test = [len(el) for el in b]
                if max(test)>1:
                    raise ValueError("b must be Nx1 Matrix (vector)")   
                else:
                    b = Matrix(b) 

            # The Gauss method consists in reducing the Matrix A 
            # to a identity form by using linear transformations, 
            # which are essentially multiplications from the left to the 
            # matrix of elementary transformations, in the end the product of
            # all these matrices gives the A^(-1) inverse matrix. Considering that all 
            # these transformations must be applied to vector b, 
            # we get A^(-1)Ax = A^(-1)b -> x = A^(-1)*b

            x = ~A*b
            print("ANSWER -> ")
            for z,k in zip(x,range(len(x))):
                print(f'x{k} = {z[0]}')
            return x
        else:
            raise TypeError(f"A and b must be list or Matrix | Your A: {type(A)}, b: {type(b)}")
            
    
    
    
    def jacobi_solver(A, b, max_iterations:int = 1000, tolerance:float=1e-6, check:bool=True):
        """
        Solve the linear system Ax = b using the Jacobi method.

        The matrix A must be strictly diagonally dominant, and it is recommended that the spectral radius
        (the maximum absolute eigenvalue) of A is less than 1 for the method to converge.

        Args:
            A (Matrix, list): The matrix A for Ax = b.
            b (Matrix, list): The right-hand side vector or matrix b. If b is a list, it should be in the format [[b1], [b2], ...].
                If b is a Matrix, it should have dimensions (n, 1).
            max_iterations (int): The maximum number of iterations. Defaults to 1000.
            tolerance (float): The tolerance of the method. Defaults to 1e-6.
            check (bool): If True, check Matrix A for spectral radius and strict diagonal dominance.

        Raises:
            ValueError: If A is not a square matrix.
            ValueError: If the determinant of A is zero or if A has infinite solutions.
            ValueError: If the shape of b is incorrect.
            ValueError: If the matrix A is not strictly diagonally dominant.
            RuntimeError: If the Jacobi method fails to converge.
            TypeError: If A or b are not of type list, Matrix, or Vector.

        Returns:
            Matrix: The result Matrix representing the solution to the linear system Ax = b.
        """
        #check for types of A and b, if list convert into Matrix
        if isinstance(A, (list,Matrix,Vector)) and isinstance(b, (list,Matrix,Vector)):
            if isinstance(A,(list,Vector)):
                if len(A) != len(A[0]):
                    raise ValueError("A must be NxN Matrix")
                else:
                    A = Matrix(A)
            if A.determinant() == 0:
                raise ValueError("Matrix determinant = 0 | inf asnwers") 
            if isinstance(b,(list,Vector)):
                test = [len(el) for el in b]
                if max(test)>1:
                    raise ValueError("b must be Nx1 Matrix (vector)")   
                else:
                    b = Matrix(b)   
            n = len(A)
            #check for spectral radius and stricly diagonally dominant matrix
            if check == True:
                for i in range(n):
                    row_sum = sum(abs(A[i][j]) for j in range(n) if j != i)
                    if abs(A[i][i]) <= row_sum:
                        raise ValueError("Your Matrix is not strictly diagonally dominant matrix")
                v = [random.random() for _ in range(n)]
                for i in range(max_iterations):
                    # Matrix-vector multiplication A*v
                    Av = [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]
                    
                    # Find the largest element of Av
                    max_av = max(Av)
                    
                    # Normalize the vector
                    v = [x / max_av for x in Av]
                    
                    # Calculate the eigenvalue as the largest element of Av
                    eigenvalue = max_av
                    
                    # Check for convergence
                    if i > 0 and abs(eigenvalue - prev_eigenvalue) < tolerance:
                        if eigenvalue >= 1:
                            warnings.warn(message=f"Yout eigenvalue is : {eigenvalue} | the sufficient convergence condition of the method is not met",category=UserWarning)
                        break
                
                    prev_eigenvalue = eigenvalue

                
            x = [0] * n
            for _ in range(max_iterations):
                x_new = [0] * n
                for i in range(n):
                    sum1 = sum(A[i][j] * x[j] for j in range(i))
                    sum2 = sum(A[i][j] * x[j] for j in range(i + 1, n))
                    x_new[i] = (b[i][0] - sum1 - sum2) / A[i][i]
                    
                if all(abs(x_new[i] - x[i]) < tolerance for i in range(n)):
                    x = Matrix([[x] for x in x])
                    print("ANSWER -> ")
                    for z,k in zip(x,range(len(x))):
                        print(f'x{k} = {z[0]}')
                    return x
                x = x_new
            raise RuntimeError("The Jacobi method did not converge")
        else:
            raise TypeError(f"A and b must be list or Matrix | Your A: {type(A)}, b: {type(b)}")
    
    
    def LU(self)->set:
        """
        Compute the LU decomposition of a square matrix.

        Raises:
            ValueError: If the matrix is not square (NxN).

        Returns:
            set: A set containing the lower triangular matrix L and the upper triangular matrix U.
                set := (L, U)
        """
        if self.rows != self.cols:
            raise ValueError("Matrix must be NxN")
        L = Matrix(self.rows,self.rows)
        U = Matrix(self.rows,self.rows)     
        
        for i in range(self.rows):
            # Верхний треугольник (матрица U)
        
            for k in range(i, self.rows):
                sum_ = 0
                for j in range(i):
                    sum_ += L[i][j] * U[j][k]
                U[i][k] = self[i][k] - sum_
        
            # Нижний треугольник (матрица L)
            for k in range(i, self.rows):
                if i == k:
                    L[i][i] = 1.0
                else:
                    sum_ = 0
                    for j in range(i):
                        sum_ += L[k][j] * U[j][i]
                    L[k][i] = (self[k][i] - sum_) / U[i][i]
        return L, U
    

    def LU_solver(A, b):
        """
        Solve a linear system Ax = b using LU decomposition.

        Args:
            A (Matrix, list[list]): The NxN matrix or list for LU decomposition.
            b (list, Matrix): If b is a list, it should be in the format [[b1], [b2], ...].
                If b is a Matrix, it should have dimensions (n, 1).

        Returns:
            Matrix: The result Matrix representing the solution to the linear system Ax = b.
        """
        if isinstance(A, (list,Matrix,Vector)) and isinstance(b, (list,Matrix,Vector)):
            if isinstance(A,(list,Vector)):
                if len(A) != len(A[0]):
                    raise ValueError("A must be NxN Matrix")
                else:
                    A = Matrix(A)
            if A.determinant() == 0:
                raise ValueError("Matrix determinant = 0 | inf asnwers") 
            if isinstance(b,(list,Vector)):
                test = [len(el) for el in b]
                if max(test)>1:
                    raise ValueError("b must be Nx1 Matrix (vector)")   
                else:
                    b = Matrix(b)   
            try:
                L,U = A.LU()
                y = [0] * A.rows
                for i in range(A.rows):
                    y[i] = (b[i][0] - sum(L[i][j] * y[j] for j in range(i))) / L[i][i]
                y = Matrix([[y] for y in y])
                x = [0] * A.rows
                for i in range(A.rows - 1, -1, -1):
                    x[i] = (y[i][0] - sum(U[i][j] * x[j] for j in range(i + 1, A.rows))) / U[i][i]
            except ZeroDivisionError:
                raise ZeroDivisionError(f"Ax=b can't be solved by LU method")
            x = Matrix([[x] for x in x])
            print("ANSWER -> ")
            for z,k in zip(x,range(len(x))):
                print(f'x{k} = {z[0]}')
            return x
        else:
            raise ValueError(f"A and b must be list or Matrix | Your A: {type(A)}, b: {type(b)}")
    
    def gauss_seidel_solver(A, b, max_iterations=1000, tolerance=1e-6,  check:bool=True):
        """
        Solve the linear system Ax = b using the least squares method.

        Args:
            A (Matrix, list): Coefficient matrix A for the system Ax = b.
            b (Matrix, list): Right-hand side vector or matrix b. If b is a list, it should be in the format [[b1], [b2], ...].
                If b is a Matrix, it should have dimensions (n, 1).

        Raises:
            ValueError: Raised if A is not a square matrix.
            ValueError: Raised if the determinant of A is zero or if A has infinite solutions.
            ValueError: Raised if the shape of b is incorrect.
            TypeError: Raised if A or b are not of type list, Matrix, or Vector.

        Returns:
            Matrix: The result vector x that solves the linear system Ax = b.
        """
        if isinstance(A, (list,Matrix,Vector)) and isinstance(b, (list,Matrix,Vector)):
            if isinstance(A,(list,Vector)):
                if len(A) != len(A[0]):
                    raise ValueError("A must be NxN Matrix")
                else:
                    A = Matrix(A)
            if A.determinant() == 0:
                raise ValueError("Matrix determinant = 0 | inf asnwers") 
            if isinstance(b,(list,Vector)):
                test = [len(el) for el in b]
                if max(test)>1:
                    raise ValueError("b must be Nx1 Matrix (vector)")   
                else:
                    b = Matrix(b)   
            n = len(A)
            if check == True:
                for i in range(n):
                    row_sum = sum(abs(A[i][j]) for j in range(n) if j != i)
                    if abs(A[i][i]) <= row_sum:
                        raise ValueError("Your Matrix is not strictly diagonally dominant matrix")
                v = [random.random() for _ in range(n)]
                for i in range(max_iterations):
                    # Matrix-vector multiplication A*v
                    Av = [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]
                    
                    # Find the largest element of Av
                    max_av = max(Av)
                    
                    # Normalize the vector
                    v = [x / max_av for x in Av]
                    
                    # Calculate the eigenvalue as the largest element of Av
                    eigenvalue = max_av
                    # Check for convergence
                    if i > 0 and abs(eigenvalue - prev_eigenvalue) < tolerance:
                            if eigenvalue >= 1:
                                warnings.warn(message=f"Yout eigenvalue is : {eigenvalue} | the sufficient convergence condition of the method is not met",category=UserWarning)
                            break
                    prev_eigenvalue = eigenvalue
            
            x = [0] * n
            for _ in range(max_iterations):
                x_new = [0] * n
                for i in range(n):
                    sum1 = sum(A[i][j] * x[j] for j in range(i))
                    sum2 = sum(A[i][j] * x[j] for j in range(i + 1, n))
                    x_new[i] = (b[i][0] - sum1 - sum2) / A[i][i]
                if all(abs(x_new[i] - x[i]) < tolerance for i in range(n)):
                    x = Matrix([[x] for x in x])
                    print("ANSWER -> ")
                    for z,k in zip(x,range(len(x))):
                        print(f'x{k} = {z[0]}')
                    return x
                x = x_new
            raise RuntimeError("The Gauss Seider method did not converge")
        else:
            raise TypeError(f"A and b must be list or Matrix | Your A: {type(A)}, b: {type(b)}")
        
    
    def leassqr_solver(A, b):
        """"Solve Ax=b with least squares  method

        Args:
            A (Matrix,list): A matrix for Ax=b
            b (Matrix, list)): b matrix for Ax = b if list b = [[b1],[b2]...] if Matrix b = Matrix(n,1)

        Raises:
            ValueError: A matrix shape
            ValueError: det=0 | inf answer error
            ValueError: b Matrix shape
            TypeError: Type error

        Returns:
            Matrix: result matrix
        """
        if isinstance(A, (list,Matrix,Vector)) and isinstance(b, (list,Matrix,Vector)):
            if isinstance(A,(list,Vector)):
                if len(A) != len(A[0]):
                    raise ValueError("A must be NxN Matrix")
                else:
                    A = Matrix(A)
            if A.determinant() == 0:
                raise ValueError("Matrix determinant = 0 | inf asnwers") 
            if isinstance(b,(list,Vector)):
                test = [len(el) for el in b]
                if max(test)>1:
                    raise ValueError("b must be Nx1 Matrix (vector)")   
                else:
                    b = Matrix(b)   
            # A^T * A
            AT = A.transpose()    
            ATA = AT * A    
            #(A^T * A)^(-1)
            ATA_inverse = ~ATA
            #(A^T * A)^(-1) * A^T
            ATA_inverse_AT = ATA_inverse*AT
            for i in range(len(A)):
                for j in range(len(A[0])):
                    for k in range(len(A)):
                        ATA_inverse_AT[i][j] += ATA_inverse[i][k] * AT[k][j]

            #x = ((A^T * A)^(-1) * A^T * b)/2
            x = [0 for _ in range(len(A[0]))]
            for i in range(len(x)):
                for j in range(len(ATA_inverse_AT[0])):
                    x[i] += (ATA_inverse_AT[i][j] * b[j][0])/2
            x = Matrix([[x] for x in x])
            print("ANSWER -> ")
            for z,k in zip(x,range(len(x))):
                print(f'x{k} = {z[0]}')
            return x
        else:
            raise TypeError(f"A and b must be list or Matrix | Your A: {type(A)}, b: {type(b)}")


    def QR(self):
        """
        Perform QR decomposition of the matrix.

        QR decomposition factorizes the matrix A into the product of two matrices Q and R,
        where Q is an orthogonal matrix and R is an upper triangular matrix.
        
        Returns:
            tuple: A tuple containing the orthogonal matrix Q and the upper triangular matrix R.
        """
        Q = Matrix(self.rows,self.cols)
        R = Matrix(self.cols,self.cols)
        for j in range(self.cols):
            v = Vector([self[i][j] for i in range(self.rows)])
            for i in range(j):
                R[i][j] = sum(Q[k][i] * v[k] for k in range(self.rows))
                for k in range(self.rows):
                    v[k] -= R[i][j] * Q[k][i]

            R[j][j] = sum(v[k] ** 2 for k in range(self.rows)) ** 0.5

            for k in range(self.rows):
                Q[k][j] = v[k] / R[j][j]

        return Q, R
    

    def QR_eigen(self, max_iterations:int=100):
        """
        Compute eigenvalues of a matrix using the QR algorithm.

        This method calculates the eigenvalues of a matrix through the QR algorithm. 
        It iteratively transforms the original matrix into an upper triangular matrix,
        which effectively approximates its eigenvalues.

        Args:
            max_iterations (int, optional): The maximum number of iterations for the QR algorithm.
                Defaults to 100.

        Returns:
            tuple: A tuple containing the following elements:
            
            - list: A list of eigenvalues approximated using the QR algorithm.
            - Matrix: The resulting upper triangular matrix after the QR algorithm.
            - Matrix: The transformation matrix containing the eigenvectors(each cols is eigenvector).

        Example:
            >>> A = Matrix([[4, 2, 2], [2, 5, 1], [2, 1, 6]])
            >>> eigenvalues, upper_triangular, eigenvectors = A.QR_eigenvalues(max_iterations=100)
            >>> print("Eigenvalues:", eigenvalues)
            >>> print("Upper Triangular Matrix (Approximation):", upper_triangular)
            >>> print("Eigenvectors:", eigenvectors)
        """
        A_k = copy.deepcopy(self)
        U_k = Matrix.identity(len(A_k))
        for k in range(max_iterations):
            Q_k_plus1, R_k_plus1 = A_k.QR() 
            A_k = R_k_plus1 * Q_k_plus1
            U_k = U_k * Q_k_plus1
        eigenvalues = Vector()
        for i in range(len(A_k)):
            eigenvalues.append(A_k[i][i])
        return eigenvalues, A_k, U_k
    
    def SVD(self, max_iterations:int = 100):
        """
        Compute the Singular Value Decomposition (SVD) of the matrix.

        Args:
            max_iterations (int, optional): Maximum number of iterations for the QR algorithm. Defaults to 100.

        Returns:
            U (Matrix): The left singular vectors as columns.
            E (Matrix): The diagonal matrix of singular values.
            V (Matrix): The transposed right singular vectors as rows.

        This function computes the SVD of the matrix using the QR algorithm. It returns the left singular vectors (U),
        a diagonal matrix of singular values (E), and the transposed right singular vectors (V).

        Usage:
        >>> A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> max_iterations = 100
        >>> U, E, V = A.SVD(max_iterations)
        """
        ATA = self.transpose()*self
        AAT = self * self.transpose()
        eigenvalues, A, V = ATA.QR_eigen(max_iterations)
        singular_values = sorted([value**0.5 for value in eigenvalues],reverse=True)
        E = Matrix.diag(singular_values, self.rows, self.cols)
        U = Matrix(self.rows,self.rows)
        VT = V.transpose()

        for i in range(len(U)):
            col = Vector([[VT[i][k]] for k in range(len(U))])
            vec = Vector([k[0] for k in ((self*col)*(1/singular_values[i])).matrix])
            U[i] = vec

        U = U.transpose()
             
        return U, E, V
