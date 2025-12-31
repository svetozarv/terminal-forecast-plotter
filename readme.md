[my_weather_app.drawio](https://github.com/user-attachments/files/24389091/my_weather_app.drawio)## What is this?
Terminal app for viewing weather forecast plots for (almost) any place on Earth.

## How to run?
```python3 terminal_user_interface.py```

Of course, you need to install prerequisites first. (Guide will appear here soon.)

## How is implemented?
[Uploading my_weather_app.drawio…](<mxfile host="app.diagrams.net" agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36" version="29.2.9">
  <diagram name="Strona-1" id="lc3qr8gt9Bfyu9D0Zx_k">
    <mxGraphModel dx="788" dy="394" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="73EQtdz4jXCsY8sIcUs6-23" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.25;exitY=0;exitDx=0;exitDy=0;entryX=1;entryY=0.75;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-1" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" value="api_session" vertex="1">
          <mxGeometry height="60" width="120" x="540" y="250" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-28" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.25;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-2" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=default;fillStyle=cross-hatch;" value="database_orm" vertex="1">
          <mxGeometry height="60" width="120" x="50" y="310" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-27" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.75;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-3" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" value="database_sto&lt;span style=&quot;background-color: transparent; color: light-dark(rgb(0, 0, 0), rgb(255, 255, 255));&quot;&gt;rage_manager&lt;/span&gt;" vertex="1">
          <mxGeometry height="50" width="200" x="100" y="220" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-18" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-19" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-4" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" value="geocoder" vertex="1">
          <mxGeometry height="60" width="120" x="630" y="140" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-17" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-15">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-5" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#cce5ff;strokeColor=#36393d;fillStyle=cross-hatch;" value="helpers" vertex="1">
          <mxGeometry height="60" width="120" x="450" y="350" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-25" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-6" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#bac8d3;strokeColor=#23445d;" value="my_weather_app" vertex="1">
          <mxGeometry height="60" width="120" x="300" y="140" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-7" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#b0e3e6;strokeColor=#0e8088;" value="tui" vertex="1">
          <mxGeometry height="60" width="120" x="300" y="50" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-32" edge="1" parent="1" source="73EQtdz4jXCsY8sIcUs6-15" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.75;entryY=1;entryDx=0;entryDy=0;" target="73EQtdz4jXCsY8sIcUs6-6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="73EQtdz4jXCsY8sIcUs6-15" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" value="plotter" vertex="1">
          <mxGeometry height="60" width="120" x="330" y="270" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>)

- `api_session.py` contains `ApiSession` class that implements the methods used to get data: `get_current_weather(lat, lon)`,`get_hourly_data(lat, lon)` and `get_daily_data(lat, lon)`. Latitude and longitude must be provided. These methods return objects of `CurrentWeather`, `HourlyWeather` and `DailyWeather` respectively, that represent the json returned by the [OpenMeteo API](https://open-meteo.com/en/docs).

- `database_orm.py` uses `peewee` to define database model

- `database_storage_manager.py` stores `DatabaseStorageManager` class that is responsible for CRUD operations on the database

- `my_weather_app.py` is the main API, combines `Plotter` and `ApiSession`.

- `plotter` uses [`plotext`](https://github.com/piccolomo/plotext) to draw plots in the terminal.

- `helpers.py` contains generic functions used in project.

- `terminal_user_interface` is a [`textual`](https://github.com/Textualize/textual) app that brings everything together.

- `geocoder.py` – module that contains 2 self explanatory functions: `city_name_to_coords()` and `coords_to_city_name()` Uses [geopy](https://geopy.readthedocs.io/en/stable/)'s [Nominatim](https://geopy.readthedocs.io/en/stable/#nominatim) to geocode coordinates and reverse the process. So called adapter between user who is writing city names and `ApiSession`, which operates exclusively on coordinates.

