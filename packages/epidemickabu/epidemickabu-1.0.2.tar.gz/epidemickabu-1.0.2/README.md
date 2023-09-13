# Kabu a new method to identify epidemic waves and their peaks and valleys

***Kabu*** is a new methodology to identify waves, peaks, and valleys from epidemic curve

## Description of files in this repository:

* `kabu.py` is the main module. It makes the necessary calculations for the subsequent identification of waves, and peaks and valleys. The main input is a dataset with two variables (i.e., **daily cases**, and **dates of report**) and the **kernel** to smooth the epidemic curve with a Gaussian filter.

* `kabuWaves.py` is a module to estimate the waves. You could set an optional **threshold** to filter the cut days and the most significant waves. There is a file called **configuration** that gives you and idea of the magnitude of this value.

* `kabuPeaksValleys.py` is a module to estimate the Peaks and Valleys. You could set an optional **threshold** to filter the cut days and the most significant peaks. There is a file called **configuration** that gives you and idea of the magnitude of this value.

## Installation

**NOTE:** *This project was made in* ***Python 3.10.6***

0. Create a folder to put the project and the virtual enviroment

1. Clone the repository inside the folder
   ```sh 
   git clone https://github.com/LinaMRuizG/Kabu.git
   ```
2. Create the virtual enviroment inside the same folder 
   ```sh 
   virtualenv venv
   ```
3. Activate the virtual environment
   ```sh 
   source /path/to/venv/bin/activate
   ```
3. Install the required libraries 
   ```sh 
   pip install -r requirements.txt
   ```


## Running

Use the `exexution.py` to run the code and set the **database path** and parameters such as **kernel**.


## Contributing

This project is in progress and it requires some improvments. Therefore, if you have any suggestion that would make this better, please fork the repository and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/improvments`)
3. Commit your Changes (`git commit -m 'Adding some improvment`)
4. Push to the Branch (`git push origin feature/improvments`)
5. Open a Pull Request

## Contact

* [Lina M Ruiz G](https://co.linkedin.com/in/lina-marcela-ruiz-galvis-465896209) - lina.ruiz2@udea.edu.co

## Acknowledgments
* [Anderson Alexis Ruales Barbosa](https://co.linkedin.com/in/anderson-alexis-ruales-b27638199?original_referer=https%3A%2F%2Fwww.google.com%2F)
* [Oscar Ignacio Mendoza Cardozo](https://loop.frontiersin.org/people/2156647/overview)

    
    
    
    
   
