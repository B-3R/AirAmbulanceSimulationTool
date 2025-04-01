import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
import geopandas as gpd
from datetime import datetime
import os
import numpy as np
import statistics
from collections import defaultdict
import matplotlib.colors as mcolors


Colors = {
    'blue-brand': '#3070B3',
    'blue-bright': '#8F81EA',
    'green': '#9FBA36',
    'grey-1': '#20252A',
    'orange': '#F7811E',
    'pink': '#B55CA5',
    'red': '#EA7237',
    'yellow': '#FED702',
    'blue-bright-dark': '#6955E2',
    'blue-dark': '#072140',
    'blue-light': '#5E94D4',
    'green-dark': '#7D922A',
    'orange-dark': '#D99208',
    'pink-dark': '#9B468D',
    'red-dark': '#D95117',
    'yellow-dark': '#CBAB01',
    'blue-bright-1': '#B6ACF1',
    'blue-dark-1': '#0A2D57',
    'blue-light-1': '#9ABCE4',
    'green-1': '#B6CE55',
    'grey-2': '#333A41',
    'orange-1': '#F9BF4E',
    'pink-1': '#C680BB',
    'red-1': '#EF9067',
    'yellow-1': '#FEDE34',
    'blue-bright-3': '#DCD8F9',
    'blue-dark-3': '#114584',
    'blue-light-3': '#D7E4F4',
    'green-3': '#D8E5A4',
    'grey-4': '#6A757E',
    'orange-3': '#FCE2B0',
    'pink-3': '#E6C7E1',
    'red-3': '#F6C2AC',
    'yellow-3': '#FEEE9A',
    'blue-bright-4': '#EFEDFC',
    'blue-dark-4': '#14519A',
    'blue-light-4': '#E3EEFA',
    'green-4': '#E9F1CB',
    'grey-7': '#DDE2E6',
    'orange-4': '#FEF4E1',
    'pink-4': '#F6EAF4',
    'red-4': '#FBEADA',
    'yellow-4': '#FEF6CD',
    'blue-bright-2': '#C9C2F5',
    'blue-dark-2': '#0E396E',
    'blue-light-2': '#C2D7EF',
    'green-2': '#C7D97D',
    'grey-3': '#475058',
    'orange-2': '#FAD080',
    'pink-2': '#D6A4CE',
    'red-2': '#F3B295',
    'yellow-2': '#FEE667',
    'blue-dark-5': '#165DB1',
    'blue-light-5': '#F0F5FA',
    'grey-8': '#EBECEF',
    'grey-9': '#FBF9FA',
    'white': '#FFFFFF',
    'black': '#000000'
}

def PlotBackground(ax,nodes,config_run,range):
    Countries = gpd.read_file("C:Geodata\\ne_50m_admin_0_countries_lakes\\ne_50m_admin_0_countries_lakes.shp")
    Rank = gpd.read_file("C:Geodata\\ne_10m_admin_1_states_provinces_scale_rank\\ne_10m_admin_1_states_provinces_scale_rank.shp")
    Countries = Countries.to_crs(epsg=3035)
    Rank = Rank.to_crs(epsg=3035)
    Rank = Rank[Rank['sr_adm0_a3'] == config_run['Geography']]

    #padding = range*1/3
    padding = 30000

    colourscheme = {'base': ['D',Colors['black']], 'hub': ['P',Colors['blue-brand']],'center': ['o',Colors['blue-brand']], 'pad': ['.',Colors['blue-light']],}

    coordinates = {}
    nodetypes = []
    routes = []

    for node in nodes:
        if node.type not in coordinates:
            coordinates[node.type] = []
            nodetypes.append(node.type)
        coordinates[node.type].append(list(node.position))
        if node.type == 'base':
            coordinates[node.type][-1].append(node.hangars)
        for node2 in nodes:
            if node != node2:
                routes.append([node.position,node2.position])

    x_min = min([node.position[0] for node in nodes]) - padding
    x_max = max([node.position[0] for node in nodes]) + padding
    y_min = min([node.position[1] for node in nodes]) - padding
    y_max = max([node.position[1] for node in nodes]) + padding

    Countries.plot(ax=ax, linewidth=1, edgecolor=Colors['black'], linestyle="-", facecolor=Colors['grey-9'], zorder=1)
    #Rank.plot(ax=ax, linewidth=1, edgecolor=Colors['blue-dark-4'], linestyle="-", facecolor=Colors['blue-light-4'], zorder=1)
    Rank.plot(ax=ax, linewidth=1, edgecolor=Colors['blue-dark-4'], linestyle="-", facecolor=Colors['grey-9'], zorder=1)

    if len(routes)<3000:
        i = 0
        for route in routes:
            if (i % 5) == 0:
                plt.plot([i[0] for i in route],[i[1] for i in route], color = Colors['grey-4'], linestyle='-', linewidth=0.5, zorder=2)

    textoffset = 8000

    for nodetype in nodetypes:
        plt.scatter([i[0] for i in coordinates[nodetype]],[i[1] for i in coordinates[nodetype]], label = nodetype, color = colourscheme[nodetype][1], marker = colourscheme[nodetype][0], zorder=4)
        if nodetype == 'base':
            labels = [f'{i[2]} vehicles' for i in coordinates[nodetype]]
            x_labels = [i[0]+ textoffset for i in coordinates[nodetype]]
            y_labels = [i[1]+ textoffset for i in coordinates[nodetype]]
            for x, y, label in zip(x_labels, y_labels, labels):
                plt.text(x, y, label, fontsize=8, color='black', zorder=4)

    plt.xlabel('Longitude (EPSG3035)')
    plt.ylabel('Latitude (EPSG3035)')
    plt.legend()
    plt.grid(True)
    plt.figtext(0.1, 0.02, "Map data © Natural Earth, naturalearthdata.com", fontsize=8, ha="left")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal', adjustable='box')

def PlotNetwork(nodes,range,config_run):
    range = 190000
    radius = range
    radius2 = range/2

    fig, ax = plt.subplots()

    PlotBackground(ax,nodes,config_run,range)
    '''
    for node in nodes:
        if node.type == 'base':
            ax.add_patch(plt.Circle(node.position, radius, facecolor=Colors['blue-light-5'], edgecolor = Colors['black'], fill=True, linewidth=1, alpha=0.22, zorder=3))
            #ax.add_patch(plt.Circle(node.position, radius2, facecolor=Colors['green-1'], edgecolor = Colors['black'], fill=True, linewidth=2, alpha=0.1, zorder=3))
    '''
    plt.title('Simulation Network')
    if False:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('results','data_log', f"result_{timestamp}_network.pdf")
        plt.savefig(filepath)
    plt.show()
    plt.close()

    return True

def Replay(nodes,vehicle_log,config_run,range):
    #Positions should be a list of time steps with a list of positions for each time step
    #vehicle_log = [[[1,[4383256.777998923,2808057.643700078],'OOS'],[2,[4383256.777998923,2808057.643700078],'IDLE']], [[1,[4483256.777998923,2808057.643700078],'OOS'],[2,[4383256.777998923,2908057.643700078],'IDLE']], [[1,[4483256.777998923,2708057.643700078],'OOS'],[2,[4383256.777998923,2808057.643700078],'OOS']]] #example vehicle log with ID, X, Y, state
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    print(f"Replay duration: {config_run['duration']/config_run['animation']['playbackspeed']} seconds")

    # only take every x-th frame to achieve framerate at given speed
    frameselector = config_run['animation']['playbackspeed']/(config_run['animation']['framerate']*config_run['timestep'])

    vehicle_log = vehicle_log[::int(frameselector)]

    fig, ax = plt.subplots()

    PlotBackground(ax,nodes,config_run,range)
    plt.title(f'Simulation Replay {config_run['animation']['playbackspeed']}x')

    colourscheme = {'OOS': Colors['grey-4'], 'IDLE': Colors['green'], 'OCCUPIED': Colors['red'], 'PATIENT': Colors['blue-light']}
    textoffset = 5000

    # Generate initial scatter plot
    id_init = [i[0] for i in vehicle_log[0]]
    x_init = [i[1][0] for i in vehicle_log[0]]
    y_init = [i[1][1] for i in vehicle_log[0]]
    color_init = [colourscheme[i[2]] for i in vehicle_log[0]]
    state_init = [i[2]+' - '+i[3] for i in vehicle_log[0]]

    clock_seconds = config_run['starttime']
    day = int(clock_seconds/(24*3600))%7
    clock_init = f'{weekdays[day]} {int((clock_seconds%(24*3600))/3600)}:{int((clock_seconds%(24*3600))/3600)} ({clock_seconds}s)'
  

    scatter = ax.scatter(x_init, y_init, c=color_init,zorder = 5,marker = '.')
    text_labels = [ax.text(x + textoffset, y + textoffset, f"{id} ({state})", fontsize=6, color='black',zorder = 5) for x, y, id, state in zip(x_init, y_init, id_init, state_init)]
    clock = ax.text(0.02,0.98,clock_init, fontsize=8, color='black',zorder = 5,transform=ax.transAxes,verticalalignment='top', horizontalalignment='left',bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    # Update function for animation
    def update(frame):
        # Extract new frame data
        x_new = [i[1][0] for i in vehicle_log[frame]]
        y_new = [i[1][1] for i in vehicle_log[frame]]
        id_new = [i[0] for i in vehicle_log[frame]]
        state_new = [i[2]+' - '+i[3] for i in vehicle_log[frame]]
        color_new = [colourscheme[i[2]] for i in vehicle_log[frame]]

        # Update scatter plot positions
        scatter.set_offsets(np.c_[x_new, y_new])
        scatter.set_color(color_new)

        # Update text labels (IDs)
        for text, x, y, new_id, new_state in zip(text_labels, x_new, y_new, id_new, state_new):
            text.set_position((x + textoffset, y + textoffset))
            text.set_text(f"{new_id} ({new_state})")
        
        if frame%(0.15*config_run['animation']['framerate']) == 0:
            clock_seconds = (frame / config_run['animation']['framerate']) * config_run['animation']['playbackspeed'] + config_run['starttime']
            day = int(clock_seconds/(24*3600))%7
            clock_text = f'{weekdays[day]} {int((clock_seconds%(24*3600))/3600)}:{int((clock_seconds%(3600))/60)} ({int(clock_seconds)}s)'
            clock.set_text(clock_text)
        return scatter, *text_labels, clock

    print(f"The replay runs {len(vehicle_log)} frames")
    # Create animation
    #ani = animation.FuncAnimation(fig, update, frames=len(vehicle_log), interval=1000/config_run['animation']['framerate'], blit=True, repeat=False)
    ani = animation.FuncAnimation(fig, update, frames=len(vehicle_log), interval=1000/config_run['animation']['framerate'], blit=True, repeat=True)
    plt.show()
    plt.close()
    return

def plot_cost_pie(costs,title):
    color_list = list(Colors.values())[:len(costs)]
    
    labels = [f"{key} ({value} €)" for key, value in costs.items()]
    values = list(costs.values())
    
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, 
                                      wedgeprops={'edgecolor': None}, colors=color_list)
    
    plt.setp(autotexts, size=10, weight='bold', color='white')
    plt.title(title)
    ax.legend(wedges, labels, loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.show()
    return

def plot_timing_pie(timing,title):
    
    color_list = list(Colors.values())[:len(timing)]

    sorted_timing = sorted(timing.items(), key=lambda item: statistics.mean(item[1]), reverse=True) #attention, makes dict into tuple
    
    labels = [f"{key} ({round(statistics.mean(value))} s)" for key, value in sorted_timing]
    values = [round(statistics.mean(value)) for key, value in sorted_timing]
    
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, 
                                      wedgeprops={'edgecolor': None}, colors=color_list)
    
    plt.setp(autotexts, size=10, weight='bold', color='white')
    plt.title(title)
    ax.legend(wedges, labels, loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.show()
    return

def plot_multiple_timing_pies(results, title):
    """
    Plots a series of pie charts, one for each fleet type, showing the median values 
    of time segments across multiple mission runs.

    Parameters:
        results (list of dicts): Each dict contains 'fleet' and 'analysis' with 'Transport Leg Time Segments'.
        title (str): Title for the entire figure.
    """

    from collections import defaultdict
    import math
    import statistics
    import numpy as np

    # Group time segments by fleet type
    fleet_data = defaultdict(lambda: defaultdict(list))
    fleet_types = []

    for result in results:
        fleet_type = ' & '.join([f'{number}x {vehicle}' for vehicle, number in result['fleet'].items()])
        if fleet_type not in fleet_types:
            fleet_types.append(fleet_type)
        timing = result['analysis']['Transport Leg Time Segments']
        for segment, value_list in timing.items():
            fleet_data[fleet_type][segment].extend(value_list)

    num_fleets = len(fleet_types)
    cols = 3
    rows = math.ceil(num_fleets / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 6, rows * 6))
    axes = axes.flatten() if num_fleets > 1 else [axes]

    plt.rcParams.update({'font.size': 10})
    fig.suptitle(title, fontsize=14)

    color_list = list(Colors.values())

    for i, fleet_type in enumerate(fleet_types):
        ax = axes[i]
        timing_data = fleet_data[fleet_type]

        # Process and rename 'cruise' to 'drive' if ambulance
        renamed_segments = {}
        for seg, values in timing_data.items():
            new_name = 'drive' if 'Ambulance' in fleet_type and seg == 'cruise' else seg
            renamed_segments[new_name] = values

        # Sort segments by median
        sorted_segments = sorted(renamed_segments.items(), key=lambda item: statistics.median(item[1]), reverse=True)

        segment_keys = [key for key, _ in sorted_segments]
        values = [round(statistics.median(value)) for _, value in sorted_segments]

        total = sum(values)
        percentages = [100 * v / total for v in values]

        # Identify the smallest segment and rename it to 'Other Segments'
        min_index = values.index(min(values))

        # Generate labels
        labels = []
        for idx, (key, pct, val) in enumerate(zip(segment_keys, percentages, values)):
            if idx == min_index:
                labels.append(f"Other Segments")
            elif pct > 5:
                labels.append(f"{key} ({round(val/60)} min)")
            else:
                labels.append("")  # hide small segments

        def autopct_filter(pct):
            return f"{pct:.1f}%" if pct > 5 else ''

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct=autopct_filter,
            startangle=140,
            wedgeprops={'edgecolor': None},
            colors=color_list[:len(values)]
        )
        ax.set_title(fleet_type)
        plt.setp(autotexts, size=9, weight='bold', color='white')

    # Hide any unused axes
    for j in range(num_fleets, len(axes)):
        axes[j].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()



def histogram(datapoints, xlabel, ylabel, title, filename, density=False, fineness=1, legend=None):
    if not isinstance(datapoints[0], list):
        datapoints = [datapoints]  # Convert single dataset into a list of lists
    
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]  # Extend as needed

    all_data = np.concatenate(datapoints)
    bins = np.histogram_bin_edges(all_data, bins='auto')
    finer_bins = np.linspace(min(bins), max(bins), int(len(bins) * fineness))

    bin_width = (finer_bins[1] - finer_bins[0]) / len(datapoints)  # Adjust width for side-by-side display

    for i, data in enumerate(datapoints):
        selected_color = color_list[i % len(color_list)]  # Pick color from list safely
        
        # Shift bins slightly so bars are next to each other
        shift = i * bin_width  
        plt.hist(data, bins=finer_bins + shift, edgecolor='black', 
                 color=selected_color, alpha=0.7, linewidth=1.2, histtype='bar', 
                 density=density, label=legend[i] if legend else None, width=bin_width)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if legend and len(datapoints) > 1:
        plt.legend()

    plt.show()

def plot_demand_distribution(joblist, config_demand):
    # Weekly distribution of demand (time of day)
    distribution = []

    for i in range(0, int(config_demand['timeframe'] / 3600)):  # Loop through hours of the week
        hourdemand = sum(1 for job in joblist if i * 3600 <= job['triggertime'] < (i + 1) * 3600)
        distribution.append(hourdemand)

    hours = np.arange(0, int(config_demand['timeframe'] / 3600))  # Full hour range

    plt.figure(figsize=(8, 5))
    plt.plot(hours, distribution, marker='', linestyle='-', linewidth=1.5, color=Colors['blue-brand'])
    plt.fill_between(hours, distribution, color=Colors['blue-brand'], alpha=0.5)

    # Set x-axis labels to show only 0,6,12,18,0 for each day
    total_days = config_demand['timeframe'] // (3600 * 24)  # Total number of days in the timeframe
    xticks = np.arange(0, len(hours), 6)  # Every 6 hours
    xtick_labels = [(i % 24) for i in xticks]  # Convert to hour of the day (0,6,12,18,0,...)

    plt.xticks(xticks, xtick_labels)  # Apply tick locations and labels

    plt.xlabel("Hour of Day")
    plt.ylabel("Demand")
    plt.title("Demand Profile")
    plt.show()

def plot_week_metric_distribution(joblist, config_demand):
    # Weekly distribution of demand (time of day)
    distribution = []

    for i in range(0, int(config_demand['timeframe'] / 3600)):  # Loop through hours of the week
        hourdemand = []
        for job in joblist:
            if i * 3600 <= job['triggertime'] < (i + 1) * 3600 and 'actualpickup' in job:
                hourdemand.append((job['actualpickup'] - job['triggertime'])/60)
        if len(hourdemand) != 0:
            hourdemand = statistics.median(hourdemand) 
        else:
            hourdemand = 0
        distribution.append(hourdemand)

    hours = np.arange(0, int(config_demand['timeframe'] / 3600))  # Full hour range

    plt.figure(figsize=(8, 5))
    plt.plot(hours, distribution, marker='', linestyle='-', linewidth=1.5, color=Colors['blue-brand'])
    plt.fill_between(hours, distribution, color=Colors['blue-brand'], alpha=0.5)

    # Set x-axis labels to show only 0,6,12,18,0 for each day
    total_days = config_demand['timeframe'] // (3600 * 24)  # Total number of days in the timeframe
    xticks = np.arange(0, len(hours), 6)  # Every 6 hours
    xtick_labels = [(i % 24) for i in xticks]  # Convert to hour of the day (0,6,12,18,0,...)

    plt.xticks(xticks, xtick_labels)  # Apply tick locations and labels

    plt.xlabel("Hour of Day")
    plt.ylabel("Median Waiting time [min]")
    plt.title("Weekly waiting time distribution")
    plt.show()

def plot_demand_map(joblist, nodes, config_run):
    fig, ax = plt.subplots()
    
    PlotBackground(ax, nodes, config_run, 0)
    plt.title('Demand Map')

    for job in joblist:
        plt.plot([job['pickup'][0], job['target'][0]], [job['pickup'][1], job['target'][1]], 'k-', linewidth=0.5)
    
    plt.show()

def plot_surface_subplots(dData, X1, X2, Y1, Y2, Z1, Z2, subGroup1, subGroup2, lSubGroup,cutoff): #dData list of dictionaries

    fig = plt.figure(figsize=(6,5.7))
    ax = fig.add_subplot(projection='3d')
    
    
    for j in range(len(lSubGroup)):
        x= []
        y= []
        z= []
        x_g= []
        y_g= []
        z_g= []
        
        for i in range(np.size(dData)):
            if dData[i][subGroup1][subGroup2] == lSubGroup[j] and dData[i][Z1][Z2] <= cutoff:
                x.append(dData[i][X1][X2])
                y.append(dData[i][Y1][Y2])
                z.append(dData[i][Z1][Z2])
            elif dData[i][subGroup1][subGroup2] == lSubGroup[j] and dData[i][Z1][Z2] > cutoff:
                x_g.append(dData[i][X1][X2])
                y_g.append(dData[i][Y1][Y2])
                z_g.append(dData[i][Z1][Z2])
                
        if len(x)>2 and len(y)>2 : #trisurf: x and y arrays must have a length of at least 3
            ax.plot_trisurf(np.array(x), np.array(y), np.array(z), alpha=0.1, color=lColors[j], edgecolor=lColors[j])
        ax.scatter(np.array(x), np.array(y), np.array(z), color=lColors[j], marker='o', alpha=1, s=8, label=lSubGroup[j])
        ax.scatter(np.array(x_g), np.array(y_g), np.array(z_g), color='#6A757E', marker='o', alpha=0.8, s=6, label=None)

    ax.legend(bbox_to_anchor=(0.5, -0.16), loc='upper center', ncol=3,columnspacing = -0.5,labelspacing=0.3)
    ax.set_xlabel(X2)
    ax.set_ylabel(Y2)
    ax.set_zlabel(Z2)
    
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.invert_xaxis()
    ax.grid(visible=True)
    plt.show()

def plot_network_performance_trend(results, metrics, units):
    """
    Creates a scatter plot with trend lines representing the median values for each metric and fleet size.
    Includes three y-axes for cost, time, and utilization metrics.

    Parameters:
        results (list of dicts): List of results containing fleet size and metric values.
        metrics (list of str): List of metric names to plot.
        units (dict): Dictionary of metric names and their corresponding units.
    """
    y_values = {}
    x_values = []
    
    # Define color scheme
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]

    # Categorize metrics into cost, time, and utilization based on unit type
    cost_metrics = [m for m in metrics if "€/km" in units.get(m, "")]
    time_metrics = [m for m in metrics if "min" in units.get(m, "") or "hour" in units.get(m, "")]
    utilization_metrics = [m for m in metrics if "%" in units.get(m, "")]

    # Get the vehicle type (assumes only one key in 'fleet')
    vehicletype = next(iter(results[0]['fleet']))

    # Initialize y_values lists for each metric
    for metric in metrics:
        y_values[metric] = {}

    # Collect data points
    for result in results:
        fleet_size = result['fleet'][vehicletype]
        x_values.append(fleet_size)
        for metric in metrics:
            if fleet_size not in y_values[metric]:
                y_values[metric][fleet_size] = []
            y_values[metric][fleet_size].append(result['analysis'][metric])

    # Create figure and main axis
    plt.rcParams.update({'font.size': 14})
    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(right=0.82,left = 0.1)
    ax1.set_xlabel('Fleet Size')

    # Create secondary y-axes
    ax2 = ax1.twinx()  # Second y-axis
    ax3 = ax1.twinx()  # Third y-axis

    # Offset the third y-axis
    ax3.spines["right"].set_position(("outward", 60))

    # Define axis labels
    ax1.set_ylabel("Cost [€/km]", color=color_list[0]) if cost_metrics else None
    ax2.set_ylabel("Time [min]", color=color_list[1]) if time_metrics else None
    ax3.set_ylabel("Utilization / Coverage [%]", color=color_list[2]) if utilization_metrics else None

    # Convert x_values to unique sorted values for trendline
    unique_x_values = sorted(set(x_values))

    # Function to plot scatter and median lines for a given axis
    def plot_metric(ax, metric_list, color):
        markers = ['D','+','P']
        for i, metric in enumerate(metric_list):
            scatter_x = []
            scatter_y = []

            median_x = []
            median_y = []

            data = [y_values[metric].get(fleet_size, []) for fleet_size in unique_x_values]

            # Plot box plot instead of scatter
            ax.boxplot(data, positions=unique_x_values, widths=0.5, patch_artist=True,
                       boxprops=dict(facecolor=color, alpha=0.5),
                       medianprops=dict(color='black', linewidth=2))

            for fleet_size in unique_x_values:
                values = y_values[metric].get(fleet_size, [])
                if values:
                    scatter_x.extend([fleet_size] * len(values))
                    scatter_y.extend(values)
                    median_x.append(fleet_size)
                    median_y.append(np.median(values))

            # Scatter plot of all values
            #ax.scatter(scatter_x, scatter_y, alpha=0.6,marker = '_', color=color_list[i % len(color_list)])

            # Plot trend line for median values
            ax.plot(median_x, median_y, marker=markers[i], linestyle='-', label=f"{metric} (Median)", color=color)

        ax.tick_params(axis='y', labelcolor=color)

    # Plot each metric category on its respective axis
    if cost_metrics:
        plot_metric(ax1, cost_metrics, color_list[0])
        ax1.set_ylim(bottom=0)
    if time_metrics:
        plot_metric(ax2, time_metrics, color_list[1])
        ax2.set_ylim(bottom=0)
    if utilization_metrics:
        plot_metric(ax3, utilization_metrics, color_list[2])
        ax3.set_ylim(bottom=0)

    # Add grid and title
    ax1.grid(True)
    plt.title(f'Network Performance - {vehicletype}')

    # Combine legends from all axes
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles3, labels3 = ax3.get_legend_handles_labels()

    ax1.legend(handles1 + handles2 + handles3, labels1 + labels2 + labels3, loc='lower left', framealpha=0.4)

    plt.show()

def plot_network_performance_trend_line(results, metrics, units): #same as above without boxplot
    """
    Creates a scatter plot with trend lines representing the median values for each metric and fleet size.
    Includes three y-axes for cost, time, and utilization metrics.

    Parameters:
        results (list of dicts): List of results containing fleet size and metric values.
        metrics (list of str): List of metric names to plot.
        units (dict): Dictionary of metric names and their corresponding units.
    """
    y_values = {}
    x_values = []
    
    # Define color scheme
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]

    # Categorize metrics into cost, time, and utilization based on unit type
    cost_metrics = [m for m in metrics if "€" in units.get(m, "")]
    time_metrics = [m for m in metrics if "min" in units.get(m, "") or "hour" in units.get(m, "")]
    utilization_metrics = [m for m in metrics if "%" in units.get(m, "")]

    # Get the vehicle type (assumes only one key in 'fleet')
    vehicletype = next(iter(results[0]['fleet']))

    # Initialize y_values lists for each metric
    for metric in metrics:
        y_values[metric] = {}

    # Collect data points
    for result in results:
        fleet_size = result['fleet'][vehicletype]
        x_values.append(fleet_size)
        for metric in metrics:
            if fleet_size not in y_values[metric]:
                y_values[metric][fleet_size] = []
            y_values[metric][fleet_size].append(result['analysis'][metric])

    # Create figure and main axis
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_xlabel('Fleet Size')

    # Create secondary y-axes
    ax2 = ax1.twinx()  # Second y-axis
    ax3 = ax1.twinx()  # Third y-axis

    # Offset the third y-axis
    ax3.spines["right"].set_position(("outward", 60))

    # Define axis labels
    ax1.set_ylabel("Cost (€)", color=color_list[0]) if cost_metrics else None
    ax2.set_ylabel("Time (min)", color=color_list[1]) if time_metrics else None
    ax3.set_ylabel("Utilization (%)", color=color_list[2]) if utilization_metrics else None

    # Convert x_values to unique sorted values for trendline
    unique_x_values = sorted(set(x_values))

    # Function to plot scatter and median lines for a given axis
    def plot_metric(ax, metric_list, color):
        markers = ['D','o','P']
        for i, metric in enumerate(metric_list):
            scatter_x = []
            scatter_y = []

            median_x = []
            median_y = []

            for fleet_size in unique_x_values:
                values = y_values[metric].get(fleet_size, [])
                if values:
                    scatter_x.extend([fleet_size] * len(values))
                    scatter_y.extend(values)
                    median_x.append(fleet_size)
                    median_y.append(np.median(values))

            # Scatter plot of all values
            #ax.scatter(scatter_x, scatter_y, alpha=0.6,marker = '_', color=color_list[i % len(color_list)])

            # Plot trend line for median values
            ax.plot(median_x, median_y, marker=markers[i], linestyle='-', label=f"{metric} (Median)", color=color)

        ax.tick_params(axis='y', labelcolor=color)

    # Plot each metric category on its respective axis
    if cost_metrics:
        plot_metric(ax1, cost_metrics, color_list[0])
        ax1.set_ylim(bottom=0)
    if time_metrics:
        plot_metric(ax2, time_metrics, color_list[1])
        ax2.set_ylim(bottom=0)
    if utilization_metrics:
        plot_metric(ax3, utilization_metrics, color_list[2])
        ax3.set_ylim(bottom=0)

    # Add grid and title
    ax1.grid(True)
    plt.title(f'Network Performance - {vehicletype}')

    # Combine legends from all axes
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles3, labels3 = ax3.get_legend_handles_labels()

    ax1.legend(handles1 + handles2 + handles3, labels1 + labels2 + labels3, loc='lower left', framealpha=0.4)

    plt.show()


def plot_network_cost_trend(results, metrics): #TODO make nicer plot
    y_values = {}
    x_values = []

    # Define color scheme
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]

    # Initialize y_values lists for each metric
    for metric in metrics:
        y_values[metric] = []
    
    # Get the vehicle type (assumes only one key in 'fleet')
    vehicletype = next(iter(results[0]['fleet']))

    # Collect data points
    for result in results:
        x_values.append(result['fleet'][vehicletype])
        for metric in metrics:
            y_values[metric].append(result['analysis'][metric])

    # Normalize all y-values (Min-Max Scaling)
    '''
    for metric in metrics:
        min_val = min(y_values[metric])
        max_val = max(y_values[metric])
        if max_val != min_val:  # Avoid division by zero
            y_values[metric] = [(val - min_val) / (max_val - min_val) for val in y_values[metric]]
        else:
            y_values[metric] = [0.5] * len(y_values[metric])  # Set to mid-scale if constant values'
    '''

    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot each metric on the same y-scale (0 to 1)
    for i, metric in enumerate(metrics):
        ax1.plot(x_values, y_values[metric], marker='.', label=metric, color=color_list[i % len(color_list)])

    # Set labels and title
    ax1.set_xlabel('Fleet Size')
    ax1.set_ylabel('Normalized Metric Value (0 - 1)')
    plt.title(f'Network Performance (Normalized) - {vehicletype}')
    
    # Format ticks and grid
    ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    plt.grid(True)

    # Add legend
    plt.legend(loc='upper right', framealpha =0.2)

    plt.show()

def plot_2D(x_values,y_values,title,x_label,y_label):
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker='.', linestyle='-', linewidth=1.5, color=Colors['blue-brand'])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    plt.show()

def plot_energy_level(vehicle_log,config_run,vehicle):

    E_level_bat = []
    E_level_gen = []
    P_current = []
    x_axis = []
    for step in range(int(config_run['duration']/config_run['timestep'])):
        x_axis.append(step*config_run['timestep'])
        E_level_bat.append((vehicle_log[step][vehicle][4])/3600000)
        E_level_gen.append((vehicle_log[step][vehicle][5])/3600000)
        P_current.append(vehicle_log[step][vehicle][6]/1000)

    plt.figure(figsize=(8, 5))
    plt.plot(x_axis, P_current, marker=',', linestyle='-', linewidth=0.7, color=Colors['blue-brand'],label = 'Current Power [kW]')
    plt.plot(x_axis, E_level_bat, marker='', linestyle='-', linewidth=1.5, color=Colors['green'],label = 'Battery Energy Level [kWh]')
    plt.plot(x_axis, E_level_gen, marker='', linestyle='-', linewidth=1.5, color=Colors['orange'],label = 'Fuel Energy Level [kWh]')

    # Set x-axis labels to show only 0,6,12,18,0 for each day
    total_days = config_run['duration'] // (3600 * 24)  # Total number of days in the timeframe
    x_hours = np.arange(0, len(x_axis)*config_run['timestep']/3600, 6)  # Every 6 hours
    xticks = np.arange(0, x_axis[-1], 6*3600)  # Every 6 hours
    xtick_labels = [abs(i % 24) for i in x_hours]  # Convert to hour of the day (0,6,12,18,0,...)

    plt.xticks(xticks, xtick_labels)  # Apply tick locations and labels
    plt.xlabel("Hour of Day [h]")
    plt.ylabel("Energy Level [kWh]/ Power [kW]")
    plt.title(f"Energy Level of Vehicle{vehicle}")
    plt.legend(loc='lower left', bbox_to_anchor=(0.02, 0.4))
    plt.show()

def plot_cost_bar(cost_dicts, titles, legs, title):

    colorlist = list(Colors.values())[:len(cost_dicts[0])]

    num_bars = len(cost_dicts)
    categories = list(cost_dicts[0].keys())
    
    # Prepare bar positions and values
    x = np.arange(num_bars)
    width = 0.6  # Bar width

    # Initialize bottom values for stacking
    bottoms = np.zeros(num_bars)

    fig, ax = plt.subplots(figsize=(8, 6))

    total_costs = [sum(cost_dict.values()) / legs[i] for i, cost_dict in enumerate(cost_dicts)]  # Total cost per bar

    for i, category in enumerate(categories):
        values = [cost_dict.get(category, 0) / legs[i] for i, cost_dict in enumerate(cost_dicts)]
        bars = ax.bar(x, values, width, label=category, bottom=bottoms, color=colorlist[i])
        
        # Add percentage text on top of each section
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if total_costs[j] > 0:  # Avoid division by zero
                percentage = (height / total_costs[j]) * 100
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height, 
                        f"{percentage:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
                
        bottoms += np.array(values)

    # Add labels and formatting
    ax.set_xticks(x)
    ax.set_xticklabels(titles, rotation=45, ha="right")
    ax.set_ylabel("Cost (€)")
    ax.set_title(title)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))

    plt.tight_layout()
    plt.show()

def plot_network_performance_heatmap(results, metric, unit, color):


    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]

    def generate_custom_colormap(base_color):
        # Convert base color to RGB
        base_rgb = mcolors.hex2color(base_color)
        white = (1, 1, 1)

        # Generate a gradient of shades (lighter to darker)
        light_rgb = [min(1, c + 0.5) for c in base_rgb]  # Lighter shade (closer to white)
        dark_rgb = [max(0, c - 0.5) for c in base_rgb]   # Darker shade

        # Create a custom colormap
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_shade", [white, base_rgb])

        return custom_cmap

    custom_cmap = generate_custom_colormap(color_list[color])


    # Extract fleet configurations and metric values from results
    fleet_size_combinations = [tuple(result['fleet'].values()) for result in results]
    metric_values = [result['analysis'][metric] for result in results]

    # Identify unique fleet types from the first result
    fleet_types = list(results[0]['fleet'].keys())

    # Extract unique values for fleet categories
    fleet_x_labels = sorted(set(fleet[0] for fleet in fleet_size_combinations))  # First fleet type values
    fleet_y_labels = sorted(set(fleet[1] for fleet in fleet_size_combinations))  # Second fleet type values

    # Create a mapping from fleet configurations to metric values
    fleet_to_metric = {fleet_size_combinations[i]: metric_values[i] for i in range(len(results))}

    # Create a 2D matrix for the heatmap
    heatmap_matrix = np.full((len(fleet_y_labels), len(fleet_x_labels)), np.nan)  # Initialize with NaN

    for i, y_label in enumerate(fleet_y_labels):
        for j, x_label in enumerate(fleet_x_labels):
            fleet_key = (x_label, y_label)
            if fleet_key in fleet_to_metric:
                heatmap_matrix[i, j] = fleet_to_metric[fleet_key]

    # Create the heatmap using Matplotlib
    plt.rcParams.update({'font.size': 14})
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(heatmap_matrix, cmap=custom_cmap, aspect="auto")#, interpolation="bicubic")

    # Add colorbar
    cbar = fig.colorbar(cax, ax=ax)
    label = f"{metric} [{unit}]"
    cbar.set_label(label)

    # Set axis labels and ticks
    ax.set_xticks(np.arange(len(fleet_x_labels)))
    ax.set_xticklabels(fleet_x_labels, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(fleet_y_labels)))
    ax.set_yticklabels(fleet_y_labels)

    xlabel = f"{fleet_types[0]} Fleet Size"
    ylabel = f"{fleet_types[1]} Fleet Size"
    ax.set_xlabel(xlabel)  # First fleet type as x-axis label
    ax.set_ylabel(ylabel)  # Second fleet type as y-axis label
    ax.set_title(f"Heatmap of {metric}")

    # Annotate cells with metric values
    for i in range(len(fleet_y_labels)):
        for j in range(len(fleet_x_labels)):
            value = heatmap_matrix[i, j]
            if not np.isnan(value):  # Only annotate valid values
                ax.text(j, i, f"{value}", ha="center", va="center", color="black")

    plt.show()


def plot_network_cost_bars(results, metrics):
    """
    Creates grouped bar charts representing the performance of various fleet types across multiple metrics.

    Parameters:
        results (list of dicts): List of results containing fleet size and metric values.
        metrics (list of str): List of metric names to plot.
    """
    y_values = {}
    fleet_types = []
    
    # Define color scheme
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink'], Colors['blue-light']]

    # Initialize y_values lists for each metric
    for metric in metrics:
        y_values[metric] = {}

    # Collect data points for each fleet type
    for result in results:
        for metric in metrics:
            fleet_type = ' & '.join([f'{number}x {vehicle}' for vehicle, number in result['fleet'].items()])
            if fleet_type not in y_values[metric]:
                y_values[metric][fleet_type] = []
            if fleet_type not in fleet_types:
                fleet_types.append(fleet_type)
            y_values[metric][fleet_type].append(result['analysis']['Cost_Breakdown_PKM'][metric])

    #print(y_values)

    # Create figure and axis
    plt.rcParams.update({'font.size': 12})
    fig, ax = plt.subplots(figsize=(12, 7))

    # Define x-axis positions
    metric_count = len(metrics)
    bar_width = 0.15  # Adjust the bar width to avoid overlap
    x_positions = np.arange(metric_count)  # Position of each metric group on x-axis

    # Plot bars for each fleet type
    for i, fleet_type in enumerate(fleet_types):
        # Get the data for the current fleet type
        fleet_data = [np.mean(y_values[metric].get(fleet_type, [0])) for metric in metrics]
        total_cost = sum(fleet_data)

        # Offset x positions for each fleet type
        x_pos_offset = x_positions + (i - (len(fleet_types) - 1) / 2) * bar_width
        
        # Plot bars for the fleet type
        bars = ax.bar(x_pos_offset, fleet_data, bar_width, label=fleet_type, color=color_list[i % len(color_list)])

        # Add value labels to each bar (in white, vertically oriented)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{height:.2f}€ ({round(100*height/total_cost)}%)', ha='center', va='bottom', rotation=90)

    # Set the x-ticks to be in the middle of each metric group
    ax.set_xticks(x_positions)
    ax.set_xticklabels(metrics)

    # Labeling
    ax.set_ylim([0, 18])
    ax.set_xlabel('Cost Share')
    ax.set_ylabel('Cost [€/km]')
    ax.set_title('Operating Cost Shares per Patient-Kilometer by Fleet Type')

    # Add a legend
    ax.legend(title='Fleet Type')

    # Display the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    Input = {'Ambulance': [['5',58.08,10.22],['5',64.25,10.57],['5',55.52,10.17],['5',58.55,9.97],['5',55.62,10.6],['5',52.09,10.25],['15',50.87,11.45],['15',50.55,11.79],['15',49.42,11.79],['15',52.51,11.66],['15',57.19,11.42],['15',50.33,11.18],['25',42.93,13.15],['25',44.62,13.05],['25',45.95,12.89],['25',50.42,12.76],['25',47.63,12.92],['25',46.27,12.41],['35',35.77,14.37],['35',36.03,14.55],['35',42.42,14.18],['35',37.7,14.09],['35',38.43,14.93],['35',37.92,13.73],['45',28.73,16.55],['45',32.92,16.8],['45',36.77,16.1],['45',36.63,16.1],['45',35.77,17.34],['45',33.91,15.43],['55',25.36,18.23],['55',28.9,18.97],['55',34.82,17.73],['55',34.07,17.62],['55',33.19,19.25],['55',31.08,17.37],['65',25.88,20.04],['65',27.37,21.25],['65',32.89,19.7],['65',26.65,19.47],['65',30.54,20.89],['65',26.33,19.12],['75',22.97,22.97],['75',28.19,24.1],['75',28.79,22.44],['75',28.51,22.13],['75',27.66,23.93],['75',26.55,22.56],['85',23.33,24.3],['85',26.29,26.11],['85',27.53,23.78],['85',24.76,23.58],['85',25.73,25.77],['85',22.12,23.61]],
            'Hybrid eVTOL': [['5',46.88,18.12],['5',47.08,18.03],['5',50.77,19.58],['5',51.13,17.4],['5',51.3,19.49],['5',41.47,17.44],['10',38.02,18.97],['10',40.72,19.46],['10',37.49,19.41],['10',41.23,18.54],['10',37.75,20.47],['10',40.5,18.89],['15',26.05,19.93],['15',27.77,21.15],['15',28.42,20.38],['15',31.33,19.88],['15',26.91,20.82],['15',27.32,19.91],['20',21.42,21.54],['20',18.52,22.21],['20',19.29,21.48],['20',19.34,21.26],['20',19.4,22.24],['20',17.2,21.13],['25',14.22,22.68],['25',13.4,23.33],['25',15.57,22.85],['25',15.62,22.68],['25',15.82,23.69],['25',15.5,22.92],['30',11.38,24.33],['30',11.25,25.33],['30',11.8,24.58],['30',11.75,24.36],['30',11.47,25.35],['30',11.38,24.45],['35',9.48,26.13],['35',9.32,27.2],['35',10.21,26.45],['35',9.35,26.05],['35',10.43,27.21],['35',9.56,26.27],['40',9.29,28.05],['40',9.37,29.1],['40',9.96,28.23],['40',9.43,27.82],['40',10.13,29.14],['40',9.21,28.17],['45',8.97,30.33],['45',9.03,31.52],['45',9.44,30.51],['45',9.05,30.07],['45',8.95,31.42],['45',8.22,30.46]],
            'Battery eVTOL': [['5',17.58,27.72],['5',18.54,27.7],['5',18.17,24.71],['5',18.47,27.66],['5',20.09,27.54],['5',16.93,27.11],['10',15.12,29.78],['10',16.07,29.44],['10',15.75,27.5],['10',16.71,30.97],['10',17.73,30.36],['10',16.62,28.83],['15',13.67,31.32],['15',15.45,30.77],['15',13.67,29.43],['15',14.03,31.73],['15',14.3,31.33],['15',13.62,30.07],['20',11.95,34.22],['20',13.35,33.56],['20',12.36,31.8],['20',11.78,34.45],['20',13.42,34.3],['20',11.88,32.86],['25',11.51,36.27],['25',11.77,34.85],['25',11.97,33.68],['25',12.38,36.42],['25',12.18,36.28],['25',11.67,34.8],['30',11.16,38.64],['30',11.28,37.87],['30',11.66,36.27],['30',11.22,39.19],['30',11.48,38.51],['30',11.16,37.46],['35',10.91,41.05],['35',10.89,40.59],['35',11.25,39.03],['35',10.84,41.45],['35',11.09,41.31],['35',10.73,40.08],['40',11.02,43.55],['40',11.15,43.11],['40',11.35,41.57],['40',10.96,44.2],['40',11.28,44.05],['40',10.88,43.35],['45',10.85,46.85],['45',11.03,46.65],['45',11.18,45.01],['45',10.65,47.67],['45',11.18,47.64],['45',10.84,46.72]],
            'Helicopter': [['5',46.86,26.33],['5',47.88,25.61],['5',47.47,26.07],['5',49.35,24.83],['5',48.3,27.38],['5',45.1,26.02],['10',33.98,26.13],['10',36.37,27.22],['10',37.63,26.87],['10',39.85,25.8],['10',37.78,28.78],['10',38.99,25.95],['15',29.18,26.47],['15',27.42,27.77],['15',27.42,26.39],['15',30.83,26.69],['15',26.72,28.06],['15',28.39,25.84],['20',20.85,27.83],['20',18.73,28.07],['20',19.72,27.26],['20',20.25,26.95],['20',20.65,28.34],['20',17.55,27.17],['25',15.85,27.78],['25',13.73,28.31],['25',15.63,27.97],['25',15.8,27.7],['25',16.37,29.03],['25',15.77,27.5],['30',11.93,28.29],['30',11.62,29.45],['30',12.63,29.02],['30',12.73,28.52],['30',12.38,29.55],['30',12.46,28.34],['35',10.57,29.35],['35',9.94,30.42],['35',10.58,30.15],['35',10.95,29.49],['35',11.07,30.72],['35',11.02,29.47],['40',10.53,30.85],['40',10.12,32.06],['40',10.52,31.57],['40',10.83,30.84],['40',10.96,32.17],['40',10.88,30.84],['45',9.51,32.45],['45',9.28,33.63],['45',9.68,33.15],['45',9.28,32.44],['45',9.41,33.85],['45',9.14,32.32]],
            'Ambulance & Hybrid eVTOL':[['10&5',43.26,15.86],['10&5',41.13,16.26],['10&5',43.1,16.58],['10&10',32.75,18.49],['10&10',26.43,19.41],['10&10',32.0,18.68],['10&15',21.93,20.41],['10&15',17.73,20.57],['10&15',19.6,20.15],['10&20',14.28,22.15],['10&20',13.38,22.7],['10&20',13.92,22.14],['20&5',33.37,16.41],['20&5',31.62,16.94],['20&5',34.68,16.4],['20&10',23.97,19.08],['20&10',20.35,19.55],['20&10',20.15,18.97],['20&15',15.72,21.04],['20&15',14.81,22.0],['20&15',15.41,21.23],['20&20',11.53,23.18],['20&20',11.24,24.46],['20&20',11.22,23.49],['30&5',28.29,17.49],['30&5',25.93,18.26],['30&5',30.75,17.61],['30&10',18.2,20.18],['30&10',17.35,21.05],['30&10',18.32,20.45],['30&15',13.86,22.53],['30&15',13.4,23.45],['30&15',12.91,22.78],['30&20',10.5,24.96],['30&20',10.58,26.06],['30&20',10.64,25.07],['40&5',25.4,19.07],['40&5',23.98,20.16],['40&5',25.47,19.05],['40&10',15.7,21.86],['40&10',15.94,23.0],['40&10',16.58,22.16],['40&15',13.13,24.19],['40&15',12.75,25.36],['40&15',12.45,24.67],['40&20',9.78,26.58],['40&20',10.22,27.91],['40&20',10.32,26.85]]}
    
    color_list = [Colors['blue-brand'], Colors['green'], Colors['orange'], Colors['yellow'], Colors['pink']]

    plt.rcParams.update({'font.size': 14})
    plt.figure(figsize=(10, 6))

    for idx, (vehicle_type, records) in enumerate(Input.items()):
        color = color_list[idx % len(color_list)]

        x_vals = []
        y_vals = []
        fleet_sizes = []

        for fleet_size, cost, time in records:
            x_vals.append(cost)
            y_vals.append(time)
            fleet_sizes.append(fleet_size)
            plt.scatter(cost, time, color=color, alpha=0.5, marker='.')

        # Sort fleet sizes: ints first, then strings
        def sort_key(fs):
            try:
                return (0, int(fs))
            except ValueError:
                return (1, fs)

        unique_sizes = sorted(set(fleet_sizes), key=sort_key)

        medians_x = []
        medians_y = []
        median_labels = []

        for fs in unique_sizes:
            fs_points = [(c, t) for s, c, t in records if s == fs]
            x_median = statistics.median([pt[0] for pt in fs_points])
            y_median = statistics.median([pt[1] for pt in fs_points])
            medians_x.append(x_median)
            medians_y.append(y_median)
            median_labels.append(fs)

            # Label median point with fleet size
            if len(unique_sizes) <10:
                plt.text(x_median + 0.5, y_median + 0.3, fs, fontsize=8, color=color,bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.8))
            else:
                plt.text(x_median - 2.5, y_median - 1.5, fs, fontsize=8, color=color, bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.1', alpha=0.8))

        # Plot median points
        if len(medians_x) <10:
            plt.plot(medians_x, medians_y, marker='D', linestyle='-',linewidth = 1.5, color=color, label=vehicle_type + ' Fleet')
        else:

            # Regression through median points
            z = np.polyfit(medians_x, medians_y, deg=3)
            p = np.poly1d(z)
            x_range = np.linspace(min(medians_x), max(medians_x), 100)
            plt.plot(x_range, p(x_range), color=color, linestyle='-', linewidth=1.5, label=vehicle_type + ' Fleet')
            plt.plot(medians_x, medians_y, marker='D', linestyle='', color=color)

        


    # Final plot styling
    plt.ylabel("Cost per Passenger Kilometer [€/km]")
    plt.xlabel("Pickup Waiting Time [min]")
    plt.title('Network Cost-Effectiveness Comparison')
    plt.grid(True)
    plt.legend(loc='upper right', framealpha=0.4)
    plt.tight_layout()
    plt.show()


    pass