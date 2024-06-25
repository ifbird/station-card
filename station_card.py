"""
A measurement station card is proposed here, it describes the most important
information of a measurement station in a standard and easily understandable way.

The information includes:
- station name
- station long name
- station location (the maps can be satellite, terrain or street)
  - location in a global map
    - location marked with star
    - show latitude and longtitude: (-90 to 90), (-180 to 180)
  - location in a country or region map
    - location marked with star
    - show state/city name with country or region name, e.g., Hyytiälä, Finland
  - local map of the station showing the measurement sites
    - measurement sites are marked with circles with unique numbers
    - the site name with height is shown near the number circle (can be above,
      below, left or right)
    - the measurement heights are usually above the ground, the tower can
      be marked by its top height
    - this map is usually plotted by person first, then the information mentioned
      above can be added as annotations
- station height level usually above the sea level
- the locations and height levels (usually above the ground level) of
  measurement sites belonging to the station
- station website and QR code if available
- station brief description including
  - type: boreal forest, tropical forest, mountain top, urban, etc.
  - established year
  - surrounding environment from close to far
  - other chracteristics
    - factors affecting the measurements
    - others
- contact persons
- organizations
- data portal website and QR code if available
- data availability
- terms of data usage
- data table including
  - name: short name or acronym
  - method: instrument with manufacturer or calculation method
  - height: meter above the ground
  - time resolution: second (S), minute (M), hour (H), day (d), month (m), year (y)
  - time period available
  - location site (refer to the location number in the measurement site map)
- acronym table
- note: some remarks if available
- reference
- version
  - card producion date and the card author with email

The information mentioned above can be put in a JSON file with the format shown
below:

{
  "name": "SMEAR II",
  "long_name": "Station for Measuring Ecosystem-Atmospere Relations II",
  "country": "Finland",
  "location": "Hyyti\u00e4l\u00e4",
  "height": "181",
  "latitude": "61.844",
  "longitude": 24.288",
  "description": "Surrounded by boreal forest",
  "sites": [
    { "1": "main cottage" },
    { "2": "mast" },
    { "3": "aerosol cottage" }
    ],
  "website": "",
  "organization": "University of Helsinki",
  "contact": "Tuukka Pet\u00e4j\u00e4 (tuukka.petaja@helsinki)",
  "data_portal": "https://smear.avaa.csc.fi",
  "data_usage_terms": "https://smear.avaa.csc.fi/terms-of-use"
  "data_table": [
    {
      "name": "temp",
      "method": "Ventilated and shielded sensor Pt-100",
      "height": "4.2, 8.4, 16.8, 33.6, 50.4, 67.2",
      "time_resolution": "1 M",
      "time_period": "1996.01.01 - ",
      "site": "2",
    },
    {
      "name": "pres",
      "method": "Druck DPI 260 barometer",
      "height": "0",
      "time_resolution": "1 M",
      "time_period": "1996.01.01 - ",
      "site": "1",
    },
    {
      "name": "PNSD",
      "method": "DMPS",
      "height": "8",
      "time_resolution": "10 M",
      "time_period": "1996.01.20 - ",
      "site": "3",
    }
    ],
  "acronym_table": [
    { "temp": "air temperature" },
    { "pres": "air pressure" },
    { "PNSD": "particle number size distribution" },
    { "DMPS": "differential mobility particle sizer" }
    ],
  "note": "",
  "reference": [
    { "Hari2005": "Hari and Kulmala, Boreal Environ. Res., 10, 315–322, 2005." },
    { "Junninen2009": "Junninen et al., Boreal Environ. Res., 14, 447–457, 2009." }
    ],
  "version": "2024.02.06, Putian Zhou (putian.zhou@helsinki.fi)"
}
"""

import os
import sys

import json

import argparse

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition
from matplotlib.gridspec import GridSpec

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from pylatex import Document, Section, Subsection, Command, \
    MiniPage, Figure, Tabular, LongTable, MultiColumn
from pylatex.utils import italic, NoEscape

# Parameters
DPI = 300


class MarkSite:
  def __init__(self, nsite, fpath_in, fpath_out):
    self.nsite = nsite
    self.fpath_in  = fpath_in
    self.fpath_out = fpath_out
    self.points = []
    self.npts = 0  # current points plotted


  def start(self):
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    res = messagebox.askquestion( \
        'Mark sites', 'Do you want to mark new sites in the local map?' \
        )

    # Create figure and axes
    self.fg, self.ax = plt.subplots(1, 1, figsize=(6, 6), \
        layout='constrained')

    if res == 'yes':
      # Load the local map PNG image
      img = mpimg.imread(self.fpath_in)

      # Put local map to subplot
      self.ax.imshow(img)
      self.ax.axis('off')  # Hide the axis
      self.fg.set_facecolor('white')

      # Connect the event
      self.cid = self.fg.canvas.mpl_connect('button_press_event', self.on_click)

      plt.show()
    # else:
    #   # Load the local map PNG image
    #   img = mpimg.imread(self.fpath_out)

    #   # Put local map to subplot
    #   self.ax.imshow(img)
    #   self.ax.axis('off')  # Hide the axis
    #   self.fg.set_facecolor('white')

    #   plt.show()
    #   # plt.pause(1.0)
    #   # plt.close('all')


  def on_click(self, event):
    """
    " Handler for mouse click events.
    """
    if not event.inaxes:
      return

    if event.xdata is None:
      return

    if event.ydata is None:
      return

    # Add the point to the list
    self.points.append((event.xdata, event.ydata))
    self.npts += 1
    
    # Plot the point
    # self.ax.plot(event.xdata, event.ydata, 'bo')
    self.ax.text(event.xdata, event.ydata, str(self.npts), \
      ha='center', va='center', \
      fontsize=12, color='white', weight='bold', \
      bbox={ \
        'boxstyle': 'circle', \
        'fc': 'white', 'ec': 'red', \
        'pad': 0.3, 'lw': 2, 'alpha': 0.4 \
        } \
      )
    
    # Update the figure
    self.fg.canvas.draw()
    
    # If three points have been added, save the figure
    if self.npts >= self.nsite:
      # Save the figure
      self.fg.savefig(self.fpath_out)

      # Disconnect
      self.disconnect()

      # Pause some time to show
      plt.pause(0.5)

      # Close the figure and continue the code
      plt.close()  # Optionally close the figure

      # Reset the variables
      self.points = []
      self.npts = 0


  def disconnect(self):
    self.fg.canvas.mpl_disconnect(self.cid)


class StationCard():
  def __init__(self, fpath_card_json):
    self.card_path = fpath_card_json
    with open(fpath_card_json) as f:
      self.card_json = json.load(f)


  def prepare_country_map(self, fabspath='./country_map.png'):

    #
    # Global and country/region maps
    #

    # Define the latitude and longitude of the location
    lat = float(self.card_json['latitude' ])
    lon = float(self.card_json['longitude'])
    
    dlat = 6.0
    dlon = 6.0

    # Create a figure
    fg = plt.figure(figsize=(6, 6), layout="constrained", dpi=DPI)

    # Create the grid
    gs = GridSpec(1, 1, figure=fg)

    # Create an axes with projection
    ax = fg.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())

    # Set extent around the location
    # (longitude_min, longitude_max, latitude_min, latitude_max)
    ax.set_extent([lon - dlon, lon + dlon, lat - dlat, lat + dlat])

    # Add features to the map
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    # ax.add_feature(cfeature.RIVERS)

    # Plot the local marker
    ax.plot( lon, lat, \
      marker='o', color='red', markersize=5, transform=ccrs.Geodetic())

    # Add information text around the local
    # name_text: area and country name
    # llh_text: latitude, longitude and height
    name_text = '{0}, {1}'.format( \
        self.card_json['location'], self.card_json['country'], \
        )
    ax.annotate( name_text, xy=(lon, lat), xycoords=ccrs.Geodetic(), \
      xytext=(0, 5), textcoords='offset points', \
      ha='center', va='bottom', \
      fontsize=12 )

    llh_text = '{0}$^\circ$ N, {1}$^\circ$ E\n{2} masl'.format( \
        self.card_json['latitude'], self.card_json['longitude'], \
        self.card_json['height'] \
        )
    ax.annotate( llh_text, xy=(lon, lat), xycoords=ccrs.Geodetic(), \
      xytext=(0, -5), textcoords='offset points', \
      ha='center', va='top', \
      fontsize=12 )

    # Add gridlines to the map
    # dms:
    # - True : show like 74o12'24" N
    # - False: show like 74.1 N
    gl = ax.gridlines( \
      crs=ccrs.PlateCarree(), draw_labels=True, dms=False, \
      linewidth=1, color='gray', alpha=0.5, linestyle='--' \
      )
    
    # Customize the gridlines
    gl.top_labels   = False  # Disable top labels
    gl.right_labels = False  # Disable right labels
    gl.xlines = True  # Draw lines for longitude
    gl.ylines = True  # Draw lines for latitude

    # Customize styles for longitude and latitude labels
    lon_formatter = LongitudeFormatter(number_format='.1f')
    lat_formatter = LatitudeFormatter(number_format='.1f')
    # ax.xaxis.set_major_formatter(lon_formatter)
    # ax.yaxis.set_major_formatter(lat_formatter)
    gl.xformatter = lon_formatter
    gl.yformatter = lat_formatter
    gl.xlabel_style = {'size': 12, 'color': 'gray', 'rotation': 45}
    gl.ylabel_style = {'size': 12, 'color': 'gray'}

    # Set position again
    # ax.set_position([0.1, 0.1, 0.4, 0.8])

    # Adding an inset with a global map
    # ax_inset = inset_axes( ax, width="50%", height="25%", loc=1, \
    #     axes_class=ccrs.PlateCarree() \
    #     )
    # ax_inset = fg.add_axes( [0.1, 0.65, 0.5, 0.25], \
    #     projection=ccrs.PlateCarree(), \
    #     transform=ax.transAxes )
    ax_inset = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax_inset.set_global()
    ax_inset.add_feature(cfeature.LAND, edgecolor='none', facecolor='grey')
    ax_inset.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax_inset.plot(lon, lat, 'ro', markersize=5, transform=ccrs.Geodetic())

    # Put the inset axes to the position relative to its parent axes
    ip = InsetPosition(ax, [0.05, 0.70, 0.5, 0.25])
    ax_inset.set_axes_locator(ip)

    # Save the figure
    fg.savefig(fabspath, dpi=DPI)

    # Close the figure
    plt.close()


  def prepare_local_map(self, fpath_local_map, fpath_local_map_new):
    nsite = len(self.card_json['sites'])
    ms = MarkSite(nsite, fpath_local_map, fpath_local_map_new)
    ms.start()


  def print_card_layout_to_figure(self, fabspath='./card.png'):
    #
    # Get some parameters
    #

    # Number of data variables, acronyms and references
    n_data = len( self.card_json['data_table'   ] )
    n_acro = len( self.card_json['acronym_table'] )
    n_ref  = len( self.card_json['reference'    ] )

    # Set number of rows for each section
    n_row = {}
    n_row['title'   ] = 1
    n_row['subtitle'] = 1
    n_row['map'     ] = 6
    n_row['desc'    ] = n_row['map']
    n_row['org'     ] = 1
    n_row['contact' ] = 1
    n_row['portal'  ] = 1
    n_row['terms'   ] = 1
    n_row['dtable'  ] = 1 + n_data
    n_row['atitle'  ] = 1
    n_row['atable'  ] = int(np.ceil(n_acro/2.0))
    n_row['note'    ] = 1
    n_row['ref'     ] = 1 + n_ref
    n_row['version' ] = 1

    # Set layout grid
    n_row_total = 0
    for k, v in n_row.items():
      n_row_total += v
    n_col_total = 3

    # Initiate the figure as A4 size
    fg = plt.figure( figsize=(8.27, 11.69), dpi=DPI, constrained_layout=True )

    # Add grids
    gs = fg.add_gridspec(n_row_total, n_col_total)

    #
    # Add axes for each section
    #
    ax = {}

    # Current row
    irow = 0

    ax['title'] = fg.add_subplot(gs[irow, :])
    irow += n_row['title']

    ax['subtitle'] = fg.add_subplot(gs[irow, :])
    irow += n_row['subtitle']

    ax['map1'] = fg.add_subplot(gs[irow:(irow+n_row['map']), 0])
    ax['map2'] = fg.add_subplot(gs[irow:(irow+n_row['map']), 1])
    ax['desc'] = fg.add_subplot(gs[irow:(irow+n_row['map']), 2])
    irow += n_row['map']

    ax['org'] = fg.add_subplot(gs[irow, :])
    irow += n_row['org']

    ax['contact'] = fg.add_subplot(gs[irow, :])
    irow += n_row['contact']

    ax['portal'] = fg.add_subplot(gs[irow, :])
    irow += n_row['portal']

    ax['terms'] = fg.add_subplot(gs[irow, :])
    irow += n_row['terms']

    ax['dtable'] = fg.add_subplot(gs[irow:(irow+n_row['dtable']), :])
    irow += n_row['dtable']

    ax['atitle'] = fg.add_subplot(gs[irow, :])
    irow += n_row['atitle']

    ax['atable'] = fg.add_subplot(gs[irow:(irow+n_row['atable']), :])
    irow += n_row['atable']

    ax['note'] = fg.add_subplot(gs[irow, :])
    irow += n_row['note']

    ax['ref'] = fg.add_subplot(gs[irow, :])
    irow += n_row['ref']

    ax['version'] = fg.add_subplot(gs[irow, :])
    irow += n_row['version']

    # Save the figure
    fg.savefig(fabspath, dpi=DPI)


class CardDocument(Document):
  def __init__(self, card_json, **kwargs):
    super().__init__(**kwargs)

    self.card_json = card_json

    # self.preamble.append(Command('title', 'Awesome Title'))
    # self.preamble.append(Command('author', 'Anonymous author'))
    # self.preamble.append(Command('date', NoEscape(r'\today')))
    # self.append(NoEscape(r'\maketitle'))
  

  def fill_document(self, fpath_country_map, fpath_local_map):
    #
    # Some parameters
    #

    # Horizontal line
    hline_text = r'\noindent\makebox[\linewidth]' + \
        r'{\rule{\textwidth}{0.4pt}}\newline'

    # Tcolorbox
    poster_arg = r'showframe, columns=3, rows=8, ' + \
        r'width=\textwidth, height=0.5\textheight, spacing=2mm'
    poster_begin = r'\begin{{tcbposter}}[poster={{{0}}}]'.format(poster_arg)
    poster_end = r'\end{tcbposter}'
    tcbset = r'\tcbset{' + \
        r'enhanced, ' + \
        r'colframe=blue!50!black, colback=white, ' + \
        r'fonttitle=\bfseries, before=, after=\hfill, ' + \
        r'boxed title style={' + \
        r'sharp corners, rounded corners=northwest, ' + \
        r'colback=tcbcolframe, boxrule=0pt,' + \
        r'}' + \
        r'}'
    
    #
    # Preamble
    #

    # Use packages
    # self.preamble.append(NoEscape(r'\usepackage{float}'))
    self.preamble.append(NoEscape(r'\usepackage{graphicx}'))
    self.preamble.append(NoEscape(r'\usepackage[table]{xcolor}'))
    # self.preamble.append(NoEscape(r'\usepackage{courier}'))
    self.preamble.append(NoEscape(r'\usepackage[most]{tcolorbox}'))
    self.preamble.append(NoEscape(r'\usepackage{array}'))
    self.preamble.append(NoEscape(r'\usepackage{tabularx}'))
    self.preamble.append(NoEscape(r'\usepackage{colortbl}'))
    self.preamble.append(NoEscape( \
      r'\usepackage[textwidth=19cm,textheight=27.5cm]{geometry}'))
    self.preamble.append(NoEscape(r'\usepackage{underscore}'))

    # Modify page layout
    # self.preamble.append(NoEscape(r'\setlength{\hoffset}{-3.5cm}'))
    # self.preamble.append(NoEscape(r'\addtolength{\textwidth}{7cm}'))
    # self.preamble.append(NoEscape(r'\setlength{\voffset}{-3.5cm}'))
    # self.preamble.append(NoEscape(r'\addtolength{\textheight}{7cm}'))

    # Other settings
    self.preamble.append(NoEscape(r'\setlength{\parindent}{0pt}'))

    #
    # Document body
    #

    # Tcolorbox settings
    self.preamble.append(NoEscape(tcbset))

    # Empty document
    self.append(NoEscape(r'\thispagestyle{empty}'))

    # Title: Station name and long name
    station_name = \
        r'\centerline{{\huge\bfseries {0}}}'.format( \
        self.card_json['name'])
    station_long_name = r'\centerline{{\large\bfseries - {0}}}'.format( \
        self.card_json['long_name'])

    self.append(NoEscape(r'\noindent'))
    self.append(NoEscape(r'\begin{tcolorbox}[boxrule=0pt,colback=white,colframe=white]'))
    self.append(NoEscape(station_name+station_long_name))
    self.append(NoEscape(r'\end{tcolorbox}'))
    self.append(NoEscape(r'\newline'))

    # Map: global map, country/region map, local map
    country_map_text = r'\includegraphics[width=0.5\linewidth]{{{0}}}'.format( \
      fpath_country_map).replace('_', '\_')
    local_map_text = r'\includegraphics[width=0.5\linewidth]{{{0}}}'.format( \
      fpath_local_map).replace('_', '\_')
    # country_map_text = r'\includegraphics[width=0.5\linewidth]{{{0}}}'.format( \
    #   fpath_country_map)
    # local_map_text = r'\includegraphics[width=0.5\linewidth]{{{0}}}'.format( \
    #   fpath_local_map)
    nsite = len(self.card_json['sites'])
    sites_text = r'\newline\textbf{Measurement sites shown in the local map}\newline'
    for i, s in enumerate(self.card_json['sites']):
      sites_text += r'{0}: {1}'.format( \
        list(s.keys())[0],list(s.values())[0])
      if i < nsite - 1:
        sites_text += r'\newline'

    self.append(NoEscape(r'\begin{tcolorbox}[title={MAP},equal height group=A,width=0.63\textwidth]'))
    self.append(NoEscape(country_map_text))
    self.append(NoEscape(local_map_text))
    self.append(NoEscape(sites_text))
    self.append(NoEscape(r'\end{tcolorbox}'))

    # Station description
    self.append(NoEscape(r'\begin{tcolorbox}[title={DESCRIPTION},equal height group=A,width=0.36\textwidth]'))
    self.append(NoEscape(self.card_json['description']))
    self.append(NoEscape(r'\end{tcolorbox}'))
    self.append(NoEscape(r'\newline'))

    # Metadata
    org_text = r'Organisation: {0}\newline '.format( \
      self.card_json['organization'])
    contact_text = r'Contact: {0}\newline '.format( \
      self.card_json['contact'])
    portal_text = r'Data portal: {0}\newline '.format( \
      self.card_json['data_portal'])
    terms_text = r'Data usage terms: {0}'.format( \
      self.card_json['data_usage_terms'])
    meta_text = org_text + contact_text + portal_text + terms_text
    self.append(NoEscape(r'\begin{tcolorbox}[title={METADATA}]'))
    self.append(NoEscape(meta_text))
    self.append(NoEscape(r'\end{tcolorbox}'))

    # Data table

    # Use @{} between to also color the column spacing
    # \extracolsep{\fill}

    # \rowcolors{starting_row}{odd_color}{even_color}
    # self.append(NoEscape(r'\rowcolors{1}{green}{pink}'))
    self.append(NoEscape(r'\begin{tcolorbox}[title={DATA TABLE}, breakable, tabularx={@{\extracolsep{\fill}\hspace{2mm}}p{1.5cm}p{5.8cm}p{3.0cm}p{1.2cm}p{3.5cm}X@{\hspace{2mm}}}, before upper pre={\rowcolors{2}{gray!10}{gray!40}}, fontupper=\scriptsize\sffamily]'))

    # Add data rows
    self.append(NoEscape(r'\textbf{name} & \textbf{method} & \textbf{height} & \textbf{tres} & \textbf{tperiod} & \textbf{site} \\'))
    self.append(NoEscape(r'\hline'))

    ndata = len(self.card_json['data_table'])
    for i, d in enumerate(self.card_json['data_table']):
      row = r'{0} & {1} & {2} & {3} & {4} & {5}'.format( \
            d['name'], d['method'], d['height'], \
            d['time_resolution'], d['time_period'], d['site'] \
            )
      if i < ndata-1:
        row += r' \\'
      self.append(NoEscape(row))

    self.append(NoEscape(r'\end{tcolorbox}'))

    # Acronym table
    self.append(NoEscape(r'\begin{tcolorbox}[title={ACRONYM TABLE},breakable,tabularx={@{\extracolsep{\fill}\hspace{2mm}}p{2.0cm}X|p{2.0cm}X@{\hspace{2mm}}},before upper pre={\rowcolors{2}{gray!40}{gray!10}}]'))

    nacr = len(self.card_json['acronym_table'])
    for i in range(0,nacr,2):
      s1 = list(self.card_json['acronym_table'][i].keys())[0]
      l1 = list(self.card_json['acronym_table'][i].values())[0]
      if i+1 < nacr:
        s2 = list(self.card_json['acronym_table'][i+1].keys())[0]
        l2 = list(self.card_json['acronym_table'][i+1].values())[0]
        row = r'{0} & {1} & {2} & {3}'.format(s1, l1, s2, l2)
      else:
        row = r'{0} & {1} & & '.format(s1, l1)

      # Only add \\ before last line
      if not ( i==nacr-1 or i+1==nacr-1 ):
        row += r' \\'

      # Append the row
      self.append(NoEscape(row))

    self.append(NoEscape(r'\end{tcolorbox}'))

    # Reference, left align
    self.append(NoEscape(r'\begin{tcolorbox}[title={REFERENCE}]'))
    nref = len(self.card_json['reference'])
    for ir, ref in enumerate(self.card_json['reference']):
      self.append(NoEscape(list(ref.values())[0]))
      if ir < nref-1:
        self.append(NoEscape(r'\newline'))
    self.append(NoEscape(r'\end{tcolorbox}'))

    # Version
    self.append(NoEscape(r'\begin{tcolorbox}[title={VERSION}]'))
    version_text = 'Version: {0}'.format(self.card_json['version'])
    self.append(version_text)
    self.append(NoEscape(r'\end{tcolorbox}'))


def do_mark_parser(args):
  print('Marking sites in a local map ...')

  # Set the card instance
  card = StationCard(args.json_file[0])
  
  # Mark site locations and then save the figure
  card.prepare_local_map(args.local_map_nomark[0], args.local_map_mark[0])


def do_card_parser(args):
  print('Generating station card ...')

  # Set the card instance
  card = StationCard(args.json_file[0])

  # Plot country map with global map inside if it does not exist
  print('- Preparing country map ...')
  if not os.path.isfile(args.country_map[0]):
    card.prepare_country_map(args.country_map[0])
  
  #
  # Create the card document
  #
  
  # print('Generating the final card pdf file ...')
  
  # Initiate
  print('- Initiating document ...')
  doc = CardDocument(
    card.card_json,
    documentclass='article',
    document_options=['a4paper', 'portrait']
    )
  
  # Call function to add text
  print('- Filling document content ...')
  doc.fill_document(args.country_map[0], args.local_map_mark[0])
  
  # Generate the pdf file
  print('- Generating pdf file ...')
  doc.generate_pdf('./card', clean_tex=False)
  
  # The document as string in LaTeX syntax, output also the tex text, the path is
  # the same as the pdf file.
  print('- Generating tex file ...')
  tex = doc.dumps()


if __name__ == '__main__':
  #
  # Set the arguments
  #

  script_desc = f"""
    Generate a station card for a measurement station.
    """
  parser = argparse.ArgumentParser(description=script_desc)
  subparsers = parser.add_subparsers(required=True)

  # subparser: mark
  mark_parser = subparsers.add_parser('mark', help='mark sites in a local map')
  mark_parser.add_argument('json_file',
    nargs=1,
    help="the path of json file containing station information"
    )
  mark_parser.add_argument('local_map_nomark',
    nargs=1,
    help="the path of local map without marks, specified by user"
    )
  mark_parser.add_argument('local_map_mark',
    nargs=1,
    help="the path of local map with marks, it can be generated by mark command"
    )
  mark_parser.set_defaults(func=do_mark_parser)

  # subparser: card
  card_parser = subparsers.add_parser('card', help='generate the card pdf file and its tex file')
  card_parser.add_argument('json_file',
    nargs=1,
    help="the path of json file containing station information"
    )
  card_parser.add_argument('country_map',
    nargs=1,
    help="the path of country map file containing location in a country scale, generated automatically if not existed"
    )
  card_parser.add_argument('local_map_mark',
    nargs=1,
    help="the path of local map with marks, it can be generated by mark command"
    )
  card_parser.set_defaults(func=do_card_parser)

  # Start to parse the arguments
  args=parser.parse_args()

  # Run the default function
  args.func(args)
