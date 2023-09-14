import a2.plotting
import a2.dataset
import numpy as np
import logging
import pathlib
import a2.cli.cli_plotting.plot as plot


FOLDER_DATA = a2.utils.file_handling.get_folder_data()
FOLDER_TWEETS = FOLDER_DATA / "tweets/"
FOLDER_WEATHER_STATIONS = FOLDER_DATA / "weather_stations/"
FOLDER_FIGURES = pathlib.Path('../../figures/')


@plot.cli.command("map")
def plot_map(
    filename_tweets=FOLDER_TWEETS
    / "tweets_no_keywords_2020-02-13T00:00:00.000Z_2020-02-14T00:00:00_locations_bba_era5.nc",
    filename_weather_stations=FOLDER_WEATHER_STATIONS / "weather_stations_hourly_rainfall_uk_2017-2020_station_number.csv",
    starting_time="2020-02-13T03:30:00.000000000",
    filename="test.pdf",
):
    import matplotlib
    matplotlib.use('PDF')
    
    logging.info(f'... loading {filename_tweets}')
    ds_tweets = a2.dataset.load_dataset.load_tweets_dataset(filename_tweets)
    ds_tweets['tp_era5_mm'] = (['index'], ds_tweets.tp_era5.values * 1e3)
    logging.info(f'... loading {filename_weather_stations}')
    df_stations = a2.dataset.load_dataset.load_weather_stations(filename_weather_stations)
    logging.info(f'... plotting')
    key_tweets = a2.dataset.tweets.KeyTweets(station_tp="tp_era5_mm")
    figure = a2.plotting.weather_maps.plot_tp_station_tweets(
        ds_tweets,
        df_stations,
        grid_shape=(5, 4),
        colormap="plasma",
        vmin=0,
        vmax=1,
        fontsize=14,
        choice_type="increment_time",
        selection_delta_time=1,
        selection_delta_time_units="h",
        selector_use_limits=[True, False],
        increment_time_delta=1,
        increment_time_delta_units="h",
        increment_time_value=np.datetime64(starting_time),
        # xlim=[-5, 0],
        # ylim=[51, 56],
        xlim=[-0.5, 0.5],
        ylim=[51, 52],
        processes=10,
        key_tweets=key_tweets,
        circle_size=0.03,
    )
    filename = FOLDER_FIGURES / "maps/stations/" / filename
    logging.info(f"... saving {filename}")
    a2.plotting.figures.save_figure(figure, filename)

