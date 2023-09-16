from setuptools import setup, find_packages

setup(name='UniMathLib',
      version='0.0.7',
      license = "GNU GPLv3",
      description="""UniMathLib is a Python library that provides essential tools for 
      working with mathematical vectors and matrices. It simplifies tasks like vector 
      and matrix operations, linear system solving, determinant calculation, and more. 
      UniMathLib offers an intuitive interface for performing mathematical operations 
      efficiently.""",
      long_description="""UniMathLib is a comprehensive Python library designed to 
      streamline mathematical operations involving vectors and matrices. Whether you're
      a mathematician, data scientist, or engineer, UniMathLib simplifies complex mathematical 
      tasks, making them accessible to everyone.

      Key Features and Functions:

      Vector and Matrix Creation: UniMathLib allows you to create vectors and matrices 
      with ease. You can initialize them with specific dimensions, lists, or even convert 
      other data types like strings, sets, tuples, or dictionaries into vectors.

      Element-Wise Operations: Perform element-wise operations on vectors and matrices 
      effortlessly. You can add, subtract, and multiply vectors and matrices, and even 
      combine them with scalars.

      Vector Distances: Calculate distances between vectors using different p-norms, including 
      the Euclidean, Manhattan, and Chebyshev norms.

      Matrix Operations: UniMathLib supports fundamental matrix operations like matrix 
      multiplication, addition, Matrix Transposition and subtraction.  You can also find 
      the determinant of a matrix or its inverse.

      Linear System Solving: Solve linear systems of equations with ease using methods 
      such as LU decomposition, Jacobi iteration, and Gauss elimination and others.

      Singular Value Decomposition (SVD): Compute the SVD of matrices, a powerful technique 
      used in various data analysis and machine learning applications.

      QR Decomposition: Perform QR decomposition of matrices, which is useful for solving 
      linear least-squares problems.

      Eigenvalues and Eigenvectors: Calculate eigenvalues and eigenvectors of matrices 
      using the QR algorithm.

      Identity and Diagonal Matrices: Create identity matrices of any size and diagonal matrices with specified diagonal values.


      UniMathLib simplifies complex mathematical tasks, making it a valuable tool for professionals and 
      students alike. Whether you need to perform basic vector operations or solve intricate linear systems,
      UniMathLib provides an efficient and user-friendly solution. Start using UniMathLib today to enhance your mathematical 
      capabilities and streamline your data analysis and computation workflows.""",
      author="Via",
      author_email="hroyango@my.msu.ru",
      packages=find_packages(),
      install_requires=[
      ],
      zip_safe=False)