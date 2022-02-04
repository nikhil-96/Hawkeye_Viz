# Hawkeye_Viz

## About this app
UK Road safety Data Visualization dashboard

## Datasets
* [Road Safety Data](https://data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data)
* We have used last 5 years (2016-2020) of Road safety data (Accidents, Casualties and Vehicles)

## Requirements

* Python 3.9.9 (add it to your path (system variables) to make sure you can access it from the command prompt)
* Git (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## How to run this app

We suggest you to create a virtual environment for running this app with Python 3. Clone this repository 
and open your terminal/command prompt in the root folder.


open the command prompt
cd into the folder where you want to save the files and run the following commands. To get the HTTPS link, press the clone button in the right top corner and then copy the link under "Clone with HTTPS". 

```
> git clone <HTTPS link>
> cd <folder name on your computer>
> python -m venv venv

```
If python is not recognized use python3 instead

In Windows: 

```
> venv\Scripts\activate

```
In Unix system:
```
> source venv/bin/activate
```

Install all required packages by running:
```
> pip == 21.2.4
> pip install -r requirements.txt
```

Run this app locally with:
```
> python index.py
```
You will get a http link, open this in your browser to see the results. You can edit the code in any editor (e.g. PyCharm) and if you save it you will see the results in the browser.

## Resources

* [Dash](https://dash.plotly.com/)
* [Plotly](https://plotly.com/python/)
* [CSS](https://codepen.io/chriddyp/pen/bWLwgP.css)
* [BOOTSTRAP](https://bootswatch.com/lux/)
