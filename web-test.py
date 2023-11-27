"""
The web-app ArDI (Advanced spectRa Deconvolution Instrument) for fitting of different types of curves. The application uses the follow packages:
1) micromap (https://github.com/romus33/micromap): time, ctypes, multiprocessing, lmfit, numpy, scipy, termcolor, os, platform

2) dash, plotly, dash_bootstrap, pandas, urllib, base64, io, os, sys, copy


Release: 0.2.0
"""
__author__ = "Roman Shendrik"
__copyright__ = "Copyright (C) 2023R"
__license__ = "GNU GPL 3.0"
__version__ = "0.2.0"

from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import finder as fnd
import numpy as np
import pandas as pd
import urllib
import base64
import io, os, sys, copy


app = Dash(__name__, external_stylesheets=
                                        [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
                                        meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}, 
                                                    {'name': 'description', 'content': 'This is the app for fitting and deconvolution of spectra'},
                                                    {'name': 'author', 'content': 'Roman Shendrik'},
                                                    {'name': 'copyright', 'content': 'Roman Shendrik'},
                                                   ]
           )
app.title = "ArDI"
app._favicon = ("assets/favicon.ico")
app.layout = html.Div([
                      html.H2('ArDI (Advanced spectRa Deconvolution Instrument)',style={'text-align': 'center'}),
             dcc.Store(id = "b"), # The container for store of the dictionary number of peaks and loaded spectrum
             dcc.Store(id = "c"), # The container for store of the dictionary with the results of fitting (curves and parameters)
             dcc.Store(id = "d"), # The container for store of the dictionary number of peaks and smoothed spectrum
             # Upload file region
             dcc.Upload(
                        id = 'upload-data',
                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                          ]),
                        style={
                                'width': '99%',
                                'justify-content': 'center',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'text-align': 'center',
                                'align-items': 'center',
                                'margin': '10px'
                                },
                        # Allow multiple files to be uploaded for future?
                        multiple = False
                    ),
             html.Div([    
                      html.H6('Look ahead:',style={'display':'inline-block','margin-left': 10, 'margin-right':5}),  
                      # Input box for peakfinder parameters
                      dbc.Input(
                                id = "lookahead",
                                type = "number",
                                value = 1,
                                placeholder = "Only integer",
                                step = 1,
                                style = {'display':'inline-block', 'width': 85,'vertical-align': 'middle'} 
                                ),
                      html.H6('Delta:',style={'display':'inline-block','margin-right':5, 'margin-left':10}),  
                      dbc.Input(
                                id = "delta",
                                type = "number",
                                value = 0.5,
                                placeholder = "",
                                step = 0.001,
                                style = {'display':'inline-block', 'width': 85,'vertical-align': 'middle'} 
                                ),
                      # Find peaks button
                      dbc.Button("Find", 
                                 color="primary", 
                                 className="me-1", 
                                 id = 'submit-val', 
                                 n_clicks = 0, 
                                 style = {"display": "inline-block",'vertical-align': 'middle', 'margin-left': '10px'}),
                      html.H6('Smooth window:',style={'display':'inline-block','margin-right':5, 'margin-left':10}),
                      ### Smooth procedures ###
                      # Moving average
                      dbc.Input(
                                id = "smooth",
                                type = "number",
                                value = 4,
                                placeholder="",
                                style={'display':'inline-block', 'width': 85,'vertical-align': 'middle'} 
                                ),                  
                      dbc.Button("Smooth", 
                                color = "primary", 
                                className = "me-2", 
                                id = 'submit-smooth', 
                                n_clicks = 0, 
                                style = {"display": "inline-block",'vertical-align': 'middle', 'margin-left': "10px"}
                                ),
                      html.H6('Als smooth p:',style={'display':'inline-block','margin-right':5, 'margin-left':10}),  
                      # Als smoothing
                      dbc.Input(
                                id = "p-als",
                                type = "number",
                                value = 0.1,
                                placeholder = "",
                                step = 0.001,
                                style={'display':'inline-block', 'width': 85,'vertical-align': 'middle'} 
                                ), 
                      html.H6('Als smooth lambda:',style={'display':'inline-block','margin-right':5, 'margin-left':10}),  
                      dbc.Input(
                                id = "lam-als",
                                type = "number",
                                value = 0.9,
                                placeholder = "",
                                style = {'display':'inline-block', 'width': 85,'vertical-align': 'middle'} 
                                ),
                      dbc.Button("Smooth Als", 
                                 color = "primary", 
                                 className = "me-2", 
                                 id = 'submit-smooth-als', 
                                 n_clicks = 0, 
                                 style = {"display": "inline-block",'vertical-align': 'middle', 'margin-left': '10px'}
                                ),
                      #Reset smoothing
                      dbc.Button("Reset", 
                                 color = "primary", 
                                 className = "me-2", 
                                 id = 'submit-reset', n_clicks=0, style={"display": "inline-block",'vertical-align': 'middle'}
                                )
                      ]),
             html.Br(),            
             html.H6('Tolerance:',style={'display':'inline-block','margin': 10,'vertical-align': 'middle'}),
             # Fittig peaks             
             dbc.Input(
                        id = "tolerance",
                        type = "number",
                        value = 1e-15,
                        placeholder = "",
                        style={'display':'inline-block', 'width': 80, 'margin': 10,'vertical-align': 'middle'} 
                       ),        
             dbc.Button("Fit", 
                            color = "success", 
                            className = "me-2", 
                            id = 'submit-fit', 
                            n_clicks = 0, 
                            style = {"display": "inline-block", 'margin-left': 5, 'margin-right':5, 'vertical-align': 'middle'}
                       ),
             # Output/input peaks          
             dbc.Input(
                        id = "peaks",
                        type = "text",
                        placeholder = "Found peaks",
                        style = {'width': '99%', 'textAlign': 'center', 'margin':'auto'}, 
                        className = "form-control form-control-sm"
                       ),
             # Plot graphs          
             html.Div([dcc.Loading(dcc.Graph(id = 'graph'), type = "circle")], 
                        style = {'width': '40%', 'display': 'inline-block'}
                        ),
             html.Div([dcc.Loading(dcc.Graph(id = 'graph_fit'), type = "cube")], 
                        style = {'width': '60%', 'display': 'inline-block'}
                     ),
             # Download inital curve with substracted baseline, fitted curve, peak curves and the best fit parameters 
             html.A(
                    'Download Subsracted Baseline Data',
                    id = 'download-link-substr',
                    download = "substr.csv",
                    href = "",
                    target = "_blank",
                    style = {'display': 'inline-block','font-family': 'Times New Roman, Times, serif', 
                            'font-weight': 'bold', 'margin-left': '10px',
                            'vertical-align': 'middle'
                            }
                    ),
             html.A(
                    'Download Fitted Data',
                    id = 'download-link-fit',
                    download = "fit.csv",
                    href = "",
                    target = "_blank",
                    style = {'display': 'inline-block', 'font-family': 'Times New Roman, Times, serif', 
                            'font-weight': 'bold', 'margin-left': '10px',
                            'vertical-align': 'middle'
                            }
                    ),
             html.A(
                    'Download Peaks',
                    id = 'download-link-peaks',
                    download = "peaks.csv",
                    href = "",
                    target = "_blank",
                    style = {'display': 'inline-block','font-family': 'Times New Roman, Times, serif', 
                            'font-weight': 'bold', 'margin-left': '10px',
                            'vertical-align': 'middle'
                            }
                    ),
             html.A(
                    'Download Fitting Parameters',
                    id = 'download-link-params',
                    download = "params.csv",
                    href = "",
                    target = "_blank",
                    style = {'display': 'inline-block','font-family': 'Times New Roman, Times, serif', 
                            'font-weight': 'bold', 'margin-left': '10px',
                            'vertical-align': 'middle'
                            }
                    ),
                    #Block with fitting parameters table
             html.Div([
                        dash_table.DataTable(
                        id='table-dropdown',
                        columns = [
                                    {'id': 'p_center', 'name': 'Center (C)'},
                                    {'id': 'p_amplitude', 'name': 'Amplitude (A)'},
                                    {'id': 'p_width', 'name': 'Sigma (S)'},
                                    {'id': 'p_method', 'name': 'Method', 'presentation': 'dropdown'},
                                    {'id': 'l_center_min', 'name': 'C_min value'},
                                    {'id': 'l_center_max', 'name': 'C_max value'},
                                    {'id': 'l_amplitude_min', 'name': 'A_min scaler'},
                                    {'id': 'l_amplitude_max', 'name': 'A_max scaler'},
                                    {'id': 'l_width_min', 'name': 'S_min scaler'},
                                    {'id': 'l_width_max', 'name': 'S_max scaler'},
                                   ],
                        editable=True,
                        dropdown={
                                    'p_method': {
                                    'options': [{'label': i, 'value': i} for i in ['PseudoVoigt', 'Gaussian', 'Voigt', 
                                                                                    'Lorentzian','Pearson4','Pearson7',
                                                                                    'DampedHarmonicOscillator','StudentsT', 
                                                                                    'Moffat','SplitLorentzian'
                                                                                  ]
                                               ]
                                                }
                                  }
                                            ),
                 html.Div(id = 'table-dropdown-container')]),
                 html.Div(
                            [
                            html.P(
                                    'Для определения максимумов пиков на спектре задаются два параметра.'
                                    ),
                            html.Ol([
                                    html.Li(
                                            'Lookahead - целое число, которое задает минимальное расстояние между пиками (по умолчанию: 1). Если пики широкие, то его можно увеличить для улучшения производительности'
                                            ), 
                                    html.Li(
                                            'Delta - задает минимальную интенсивность пика. Связана с соотношением сигнал/шум на спектре. Чем выше это отношение, тем меньше она может быть задана. Неправильный выбор этой величины приводит к нахождению ложных пиков.'
                                            ), 
                                    ]),                                    
                            html.P(
                                    'Деконволюция спектра проводится по методу наименьших квадратов. Входными параметрами для процедуры подгонки являются следующие для каждого из пиков.'
                                    ), 
                            html.Ol([
                                    html.Li('Предполагаемые координаты центров пиков (С),'), 
                                    html.Li('Предполагаемая интегральная амплитуда пика (A),'), 
                                    html.Li('Предполагаемая сигма для пика (S)'), 
                                    html.Li('Форма пика (выбирается из выпадающего списка).')
                                    ]),
                            html.P('Также задаются ограничения на область значений при подгонке пиков:'), 
                            html.Ol([
                                     html.Li(
                                            'C_min value, C_max values. Значения координаты центра пика будут находится в соответствующем интервале [С-С_min; C+C_max]'
                                            ),
                                     html.Li(
                                            'A_min scaler, A_max scaler. Значения амплитуды каждого из пиков будут находится в соответствующем интервале [A*A_min; A*A_max]'
                                            ), 
                                     html.Li(
                                            'S_min scaler, S_max scale. Значения сигмы каждого из пиков будут находится в соответствующем интервале [S_min*S; S_max*S].'
                                            ),
                                     ]),
                            html.P(
                                    'Все эти 10 параметров задаются для каждого из пиков. По умолчанию значения каждого из параметров одинаковое для всех пиков и приведены в таблице. Однако для каждого из пика их можно изменять прямо в таблице. После изменения нажимается клавиша ввод и тогда значение измененного параметра будет учитываться при подгонке.')], 
                                    id = 'instruction'
                                    )
                            ],
                            style = {'display': 'inline-block','margin-left':'10px','margin-right':'10px','margin-top': '10px'}
                            )

"""
Code of callback for web-interface
"""
# Upload file callback
@app.callback(
                [Output('b', 'data'),
                Output('d', 'data')],
                Input('upload-data', 'contents'),
                State('upload-data', 'filename'),
                prevent_initial_call = True
            )

    
def parse_contents(contents,filename):
    """
            Input:
                contents: the uploaded file content
                filename (str): the uploaded filename
            Output:
                c_ (dict): the dictionary with the following structure:
                spectra['spectrum']=[xx,yy] (array)   - 2D array with x and y coordinates of the uploaded spectrum
                spectra['peaks']=x          (array) - list contains x-coordinates of found maxima
                spectra['look']=lookahead   (int)   - lookahead parameter of peakdetect
                spectra['delta']=delta      (float) - delta parameter of lambda
                spectra['ampl']=ampl        (arrray) - array of maxima amplitudes (y-coordinates).
                The dictionaries are stored in b and d containers
            Note: 
                Parse content of the uploaded file with spectrum. In the version 0.2.0 the follow format is supported:
                .esp - ASCII format from EnSpectr. The first two rows should be skipped. The file contains two columns separated by space
                .txt - ASCII format from Horiba. The file contains two columns separated by tab.
                .csv - The csv format.
                The xls formats prepared in russian Excel contain the illegal symbols but they could be supported in the future.
                After reading of the file the starting peak detecion with lookahead=1, delta=0.5 is performed.
    """

        
    c_={}
    if '.esp' in filename:
            content_type,content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            dec_ = io.StringIO(decoded.decode('utf-8'))
            res_ = dec_.getvalue().splitlines()
            c_ = fnd.readfile(res_,skiprows=2)
    elif '.txt' in filename:
                decoded = base64.b64decode(contents).decode(errors='ignore')
                res_= decoded.splitlines()
                c_ = fnd.readfile(res_)
            
    elif '.csv' in filename:
                print(filename)
                content_type,content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                res_ = pd.read_csv(io.StringIO(decoded.decode('utf-8'))).values.tolist()
                res_ = [str(i[0])+' '+str(i[1]) for i in res_]
                c_ = fnd.readfile(res_)
    else:
                raise ValueError(f'Format of file is not supported.')
    return (c_, c_)

# Plot the uploaded spectrum callback       
@app.callback(

                Output('table-dropdown', 'data'),
                Output('graph', 'figure'),
                Output('lookahead', 'value'),
                Output('delta', 'value'),
                Output('peaks', 'value'),
                [Input('b', 'data')],
                prevent_initial_call = True,
            )
        
def update_line_chart(contents):
    """
            Input:
                contents (dict): the dictionary with the following structure:
                c_ (dict): the dictionary with the following structure:
                spectra['spectrum']=[xx,yy] (array)   - 2D array with x and y coordinates of the uploaded spectrum
                spectra['peaks']=x          (array) - list contains x-coordinates of found maxima
                spectra['look']=lookahead   (int)   - lookahead parameter of peakdetect
                spectra['delta']=delta      (float) - delta parameter of lambda
                spectra['ampl']=ampl        (arrray) - array of maxima amplitudes (y-coordinates).
                The dictionary is uploaded from the b container.                
            Output:
                params (list): list containing the generated fitting parameters for table-dropdown object. The number of elements in the list is the number of peaks. Every element of the list is dictionary with the following structure:
                {'p_center': value, 'p_amplitude': data_['ampl'][num], 'p_width': 4,'p_method': 'PseudoVoigt', 'l_center_min': 5, 'l_center_max': 5, 'l_amplitude_min': 0, 'l_amplitude_max': 1000, 'l_width_min': 0.2, 'l_width_max':20}
                fig (dict) - dictionary for plot figure
                data_['look'] (int): the value of lookahead parameter of peakfit
                data_['delta'] (float): the value of lambda parameter of peakfit
                peaks (list):           the list of the peaks
            Note: 
                Plot the uploaded spectrum and found peaks.
    """

    data_=contents
    fig = go.Figure()
    fig = fig.add_trace(go.Scatter(x = data_['spectrum'][0], y = data_['spectrum'][1],
                                    mode = 'lines',
                                    name = 'Initial spectrum'
                                    )
                        )
                    
    for i in data_['peaks']:
        fig.add_vline(x = i, line_width = 3, line_dash="dash", line_color = "green")
    params = []
    for num, value in enumerate(data_['peaks']):
        params.append(
                        {'p_center': value, 'p_amplitude': data_['ampl'][num], 
                        'p_width': 4,'p_method': 'PseudoVoigt', 'l_center_min': 5, 
                        'l_center_max': 5, 'l_amplitude_min': 0, 'l_amplitude_max': 1000, 
                        'l_width_min': 0.2, 'l_width_max':20
                        }
                      )
    return params, fig, data_['look'], data_['delta'], ','.join([str(round(i)) for i in data_['peaks']])

# Find peaks again with new lookahead and lambda parameters    
@app.callback(
                [Output('b', 'data',allow_duplicate = True)],
                Input('submit-val', 'n_clicks'),
                [State('b', 'data')],
                State('lookahead', 'value'),
                State('delta', 'value'),
                prevent_initial_call = True,
            )

def reparse(n_clicks, res_, lookahead, delta):
    return [fnd.peakdetect(res_['spectrum'][0],res_['spectrum'][1],lookahead,delta)]

# Add or remove peaks manually callback       
@app.callback(
                [Output('b', 'data',allow_duplicate = True)],
                Input('peaks', 'n_submit'),
                State('peaks', 'value'),
                [State('b', 'data')],
                prevent_initial_call = True,
             )

def change_peaks(n_submit, peaks_str, old_data):
    # Read Input box "peaks" with updated peaks maxima and rewrite the b container
    peaks = [int(i) for i in peaks_str.split(',') if i.strip().isdigit()]
    ampl = []
    for i in peaks:
        ampl.append(1)
    data_ = old_data
    data_['peaks'] = peaks
    data_['ampl'] = ampl
    return [data_]

# Smooth spectrum using weighted average method callback        
@app.callback(
                [Output('b', 'data',allow_duplicate = True)],
                Input('submit-smooth', 'n_clicks'),
                [State('b', 'data')],
                State('smooth', 'value'),
                prevent_initial_call = True,
            )

def smooth(n_clicks, res_, smooth):
        smooth_data = fnd.smooth(res_['spectrum'][1],smooth)
        c_ = res_
        c_['spectrum'][1] = smooth_data
        return [c_]

# Smooth spectrum using ALS method callback
@app.callback(
                [Output('b', 'data',allow_duplicate = True)],
                Input('submit-smooth-als', 'n_clicks'),
                [State('b', 'data')],
                State('p-als', 'value'),
                State('lam-als', 'value'),
                prevent_initial_call = True,
              )

def smooth_als(n_clicks, res_, p_als, lam_als):
        smooth_data = fnd.smooth_als(res_['spectrum'][1], p_als, lam_als)
        c_ = res_
        c_['spectrum'][1] = smooth_data
        return [c_]        
# Reset smoothing callback. Return uploaded spectrum
@app.callback(
                [Output('b', 'data',allow_duplicate = True)],
                Input('submit-reset', 'n_clicks'),
                [State('d', 'data')],
                prevent_initial_call = True,
              )

def reset_data(n_clicks, res_):
    return [res_]

# Update figure after re-peakdetect        
@app.callback(
                Output('graph', 'figure',allow_duplicate = True),
                Output('lookahead', 'value',allow_duplicate = True),
                Output('delta', 'value',allow_duplicate = True),
                Output('peaks', 'value',allow_duplicate = True),
                [Input('b', 'data')],
                State('upload-data', 'filename'),
                prevent_initial_call = True,
              )
        
def update_line_chart(data_, filename):

    fig = go.Figure()
    fig = fig.add_trace(go.Scatter(x = data_['spectrum'][0], 
                                   y = data_['spectrum'][1],
                                   mode = 'lines',
                                   name = 'Initial spectrum'
                                   ), 
                        )
    for i in data_['peaks']:
        fig.add_vline(x = i, line_width = 3, line_dash = "dash", line_color = "green")
    fig.update_layout(
                        title = "Spectrum from file: "+filename,
                        xaxis_title = "Wavenumber, cm-1",
                        yaxis_title = "Intensity"
                     )   
    return fig, data_['look'], data_['delta'], ','.join([str(round(i)) for i in data_['peaks']])

# Fit procedure callback
@app.callback(
                Output('graph_fit', 'figure'),
                Output('download-link-substr', 'href'),
                Output('download-link-fit', 'href'),
                Output('download-link-peaks', 'href'),
                Output('download-link-params', 'href'),
                Input('submit-fit', 'n_clicks'),
                State('peaks', 'value'),
                [State('b', 'data')],
                State('upload-data', 'filename'),
                State('tolerance','value'),
                State('table-dropdown','data'),
                prevent_initial_call = True,
            )
    
def update_fitline_chart(n_clicks, peaks, data_, filename, tolerance,table_par):

    data_ = fnd.fitcurve(data_['spectrum'][0],data_['spectrum'][1],peaks, parameters=table_par, tolerance=tolerance)
    fig = go.Figure()
    df_peaks = {}
    df_peaks['x'] = data_['output'][0]
    df_conv = {'x': data_['output'][0], 'y': data_['output'][1]}
    bg_ = np.array([])
    fig = make_subplots(rows = 2, cols = 1,row_heights = [90,10],subplot_titles=['','Residual'])
    # Plot the initial spectrum
    fig = fig.add_trace(go.Scatter(
                                    x = data_['input'][0], 
                                    y = data_['input'][1],
                                    mode = 'lines',
                                    name = 'Initial spectrum'
                                    ),
                                    row = 1,
                                    col = 1
                        )
    # Plot the best fit curve                   
    fig = fig.add_trace(go.Scatter(
                                    x = data_['output'][0], 
                                    y = data_['output'][1],
                                    mode = 'lines',
                                    name = 'Fitted spectrum'
                                    ),
                                    row = 1,
                                    col = 1
                        )
    # Plot fitted components                    
    for model_name, model_value in data_['components'].items():
        fig = fig.add_trace(go.Scatter(
                                        x = data_['output'][0], 
                                        y = model_value,
                                        mode='lines',
                                        name = model_name
                                        ),
                                        row = 1,
                                        col = 1
                            )
        if model_name == 'bg_': 
                bg_ = model_value
        df_peaks[str(model_name)] = model_value
    # Plot residual    
    fig = fig.add_trace(go.Scatter(
                                   x = data_['input'][0], 
                                   y = data_['output'][1]/data_['input'][1]-1,
                                   mode = 'lines'
                                   ),
                                   row = 2,
                                   col = 1
                        )
    # Prepare data for csv
    df_substr = {'x': data_['input'][0], 'y': data_['input'][1]-bg_}
    df = pd.DataFrame(data = df_substr)
    csv_string_s = df.to_csv(index = False, encoding = 'utf-8')
    csv_string_s = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string_s)
    df = pd.DataFrame(data=df_conv)
    csv_string_f = df.to_csv(index = False, encoding = 'utf-8')
    csv_string_f = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string_f)
    df = pd.DataFrame(data = df_peaks)
    csv_string_p = df.to_csv(index = False, encoding = 'utf-8')
    csv_string_p = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string_p)
    df_ = pd.DataFrame(data = data_['params'])
    csv_string_pa = df_.to_csv(index = False, encoding = 'utf-8')
    csv_string_pa = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string_pa)    
    fig.update_layout(title = "Deconvoluted spectrum of "+filename+". R-Square: {0:.4f}".format(data_["params"]["R-Square"]),
    xaxis_title = "Wavenumber, cm-1",
    yaxis_title = "Intensity")   
    return fig, csv_string_s, csv_string_f, csv_string_p, csv_string_pa 

    
app.run_server(debug = True)