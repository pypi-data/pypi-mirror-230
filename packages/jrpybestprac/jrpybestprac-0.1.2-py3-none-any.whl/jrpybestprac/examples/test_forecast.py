# Content of test/test_forecast.py
def weather_forecast(weather="rain"):
    return "Tomorrow will be: " + weather


def test_answer():
    assert "rain" in weather_forecast()
