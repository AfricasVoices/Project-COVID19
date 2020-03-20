import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import LinearSegmentedColormap
from shapely.algorithms.polylabel import polylabel


class MappingUtils(object):
    @staticmethod
    def render_map(geo_data, id_key, frequencies):
        """

        :param geo_data:
        :type geo_data:
        :param id_key:
        :type id_key:
        :param frequencies:
        :type frequencies:
        :return:
        :rtype:
        """
        map_frequencies = []
        for k, v in frequencies.items():
            map_frequencies.append({
                id_key: k,
                "Frequency": v if v != 0 else None
            })

        geo_data = geo_data.merge(pandas.DataFrame(map_frequencies), on=id_key)

        avf_color_map = LinearSegmentedColormap.from_list("avf_color_map", ["#e6cfd1", "#993e46"])
        geo_data.plot(column="Frequency", scheme="fisher_jenks", k=5, cmap=avf_color_map,
                      linewidth=0.25, edgecolor="black", missing_kwds={"edgecolor": "black", "facecolor": "white"})
        plt.axis("off")

        for i, county in geo_data.iterrows():
            # largest_polygon = max(county.geometry, key=lambda p: p.area)
            # print(polylabel(largest_polygon, 20).coords[0])
            plt.annotate(s=frequencies[county[id_key]],
                         xy=(county.label_x, county.label_y),
                         ha='center', va="center", fontsize=3.8)


