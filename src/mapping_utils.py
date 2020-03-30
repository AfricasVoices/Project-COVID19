import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import LinearSegmentedColormap


class MappingUtils(object):
    AVF_COLOR_MAP = LinearSegmentedColormap.from_list("avf_color_map", ["#e6cfd1", "#993e46"])

    @classmethod
    def plot_frequency_map(cls, geo_data, admin_id_column, frequencies, label_position_columns=None,
                           callout_position_columns=None):
        """
        Plots a map of the given geo data with a choropleth showing the frequency of responses in each administrative
        region.

        The map is plotted to the active matplotlib figure. Use matplotlib.pyplot to access and manipulate the result.

        :param geo_data: GeoData to plot.
        :type geo_data: geopandas.GeoDataFrame
        :param admin_id_column: Column in `geo_data` of the administrative region ids.
        :type admin_id_column: str
        :param frequencies: Dictionary of admin_id -> frequency.
        :type frequencies: dict of str -> int
        :param label_position_columns: A tuple specifying which columns in the `geo_data` contain the positions to draw
                                       each frequency label at, or None.
                                       The format is (X Position Column, Y Position Column). Positions should be in
                                       the same coordinate system as the geometry, and represent the vertical and
                                       horizontal center position of the drawn label.
                                       If None, no frequency labels are drawn.
        :type label_position_columns: (str, str) | None
        :param callout_position_columns: A tuple specifying which columns in the `geo_data` contain the positions to
                                         draw callout lines to, or None.
                                         The format is (X Position Column, Y Position Column). Positions should be in
                                         the same coordinate system as the geometry, and represent the target location
                                         to draw the callout line to. The callout line is drawn from the label_position
                                         for this feature.
                                         If None, no callout lines are drawn.
        :type callout_position_columns: (str, str) | None
        """
        # Convert the raw frequencies dict to a pandas DataFrame, then join it with the geo data frame on the admin_ids.
        # Frequencies that are 0 are set to None ('missing'), to prevent the color-mapping algorithm including
        # low responses (e.g. just 1 or 2) in the same class (color) as regions with no response.
        map_frequencies = []
        for k, v in frequencies.items():
            map_frequencies.append({
                admin_id_column: k,
                "Frequency": v if v != 0 else None
            })
        geo_data = geo_data.merge(pandas.DataFrame(map_frequencies), on=admin_id_column)

        # Plot the choropleth map.
        # Frequencies are classed using the Fisher-Jenks method, a standard GIS algorithm for choropleth classification.
        # Using this method prevents a region with a vastly higher frequency than the others (e.g. a capital city)
        # from using up all of the colour range, as would happen with a linear scale.
        unique_frequencies = {f for f in frequencies.values() if f != 0}
        number_of_classes = min(5, len(unique_frequencies))
        if number_of_classes > 0:
            geo_data.plot(column="Frequency", cmap=cls.AVF_COLOR_MAP,
                          scheme="fisher_jenks", k=number_of_classes,
                          linewidth=0.1, edgecolor="black",
                          missing_kwds={"edgecolor": "black", "facecolor": "white"})
        else:
            # Special-case plotter for when all frequencies are 0, because geopandas crashes otherwise.
            geo_data.plot(linewidth=0.1, edgecolor="black", facecolor="white")
        plt.axis("off")

        # Add a label to each administrative region showing its absolute frequency.
        # The font size is currently hard-coded for Kenyan counties.
        # TODO: Modify once per-map configuration needs are better understood by testing on other maps.
        if label_position_columns is not None:
            for i, admin_region in geo_data.iterrows():
                # Set label and callout positions from the features in the geo_data,
                # translating from the geo_data format to the matplotlib format.
                if callout_position_columns is None or pandas.isna(admin_region[callout_position_columns[0]]):
                    # Draw label only.
                    xy = (admin_region[label_position_columns[0]], admin_region[label_position_columns[1]])
                    xytext = None
                else:
                    # Draw label and callout line.
                    xy = (admin_region[callout_position_columns[0]], admin_region[callout_position_columns[1]])
                    xytext = (admin_region[label_position_columns[0]], admin_region[label_position_columns[1]])

                plt.annotate(s=frequencies[admin_region[admin_id_column]],
                             xy=xy, xytext=xytext,
                             arrowprops=dict(facecolor="black", arrowstyle="-", linewidth=0.1, shrinkA=0, shrinkB=0),
                             ha="center", va="center", fontsize=3.8)
