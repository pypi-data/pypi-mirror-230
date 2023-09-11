# ![Image](./_d29623d8-088c-480c-8d70-0b831a2c23a6.jpg "PythonCoordinates") PythonCoordinates

During the development of code to construct the source noise directivity patterns from my dissertation, it became 
apparent that on limitation of coding of physical elements was units. Whether it was the code I wrote myself, or 
what I found online it was difficult to know the specific units that we expected, and how to convert them for the 
appropriate unit base used within the function.

In addition to units, there is the locating of the objects in 3-space, how to move and rotate them. And just as 
important how two or more were related. This Python module provides access to the appropriate linear algebra equations,
a series of measurement objects, and the coordinates that can represent a location in 3-space. These coordinates were
extended to represent the real world, providing an interface for converting the geodesic(latitude/longitude) to 
geodetic(UTM) coordinate descriptions. 

This code is part of a larger sweet of tools for the determination of physical phenomena that propagate through the
atmosphere from a source to a receiver.

Dr. Frank Mobley

This code was cleared for public release on 15 March 2023 with originator Reference Number: RH-23-124158, Case Reviewer: 
Katie Brakeville using Case Number: AFRL-2023-1262

In May 2023, the code that converts a sparse matrix to a dense matrix using nearest neighbor, bi-linear interpolation 
was added to the package. This code originates with the Mobley, Frank S., Alan T. Wall, and Stephen C. Campbell. 
__Translating jet noise measurements to near-field level maps with nearest neighbor bilinear smoothing interpolation.__
The Journal of the Acoustical Society of America 150.2 (2021): 687-693 paper. When using this code, please reference 
this article.

# Usage
## Conversion of Temperature Units

	from PythonCoordinates.measurables.physical_quantities import Temperature
	
	t = Temperature(59, Temperature.Units.Fahrenheit)
	print(t.kelvin)
	
