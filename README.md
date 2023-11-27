# ArDi
The web application is designed for curve deconvolution and fitting. It enables the deconvolution of FTIR, Raman, and luminescence spectra.

The web application is initiated using web-test.py. The web application is located at 127.0.01:8050.

The application is built on the Dash framework. The curve fitting utilizes the least-square method implemented in the lmfit package. The baseline is calculated using the ALS algorithm, and a C++ library is employed for this purpose.

The necessary packages for the application include: numpy, lmfit, plotly, dash, pandas, platform, pathlib, urllib, dash_bootstrap_components, and >glibc-2.29.

