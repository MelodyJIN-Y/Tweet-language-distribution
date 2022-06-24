<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->



<!-- PROJECT LOGO -->
<br />
<div align="center">
<h1 align="center"> Language distribution of Tweet </h1>

</div>

<!-- ABOUT THE PROJECT -->
## About The Project
This is a group project for COMP90024 Cluster and Cloud Computing (Semester 1, 2022), The University of Melbourne. The objective of this project is to read a big file (20Gb+ JSON file) containing information about tweets and calculate the number of tweets and languages used in each given cell of Sydney. The whole process is divided into two main steps. The first step is reading and extracting information about locations and languages parallelly. The second step is classifying locations into different cells and counting the number of languages used. The final output is in a CSV file with columns including cell name, number of total tweets, number of languages used and top ten languages and their corresponding number of tweets.


   * ### Parallelized processing 
   The primary method to read a big file without crashing the computer is loading some small parts of the file instead of loading all data into memory at one time. Thus, we utilize the “mmap (Memory-mapped file)” module in Python to read one record at a time. Firstly, the mmap constructor is used to open the big twitter file to create a memory-mapped file. A memory- mapped file is a mmap object, and the accountable unit in this file is the byte. The most critical point in this project is that the mmap object has indexes, so it is easy to separate parts for different MPI processes according to corresponding indexes of bytes. The “readline()” method of the mmap object can automatically read one record with an ending of “\n”. It is also an iterative step to read records one by one. As a result, the required memory space is minimal. The computer reads only one complete record into memory in each MPI process in dictionary format for further processing. Then the values of coordinates and language are extracted from their keys. These steps run simultaneously on different MPI processors. Finally, all extracted data are gathered to rank 0. Further cell allocation algorithms will do calculations about these gathered data on the root processor (rank 0).

   * ### Cell allocation
   We define a class to represent each cell in the grid. The cell class is aware of its coordinates and borders. There are different functions to test whether a given point lies on the valid border or within a cell. To cover different situations for cells on the grid border, we define cells whose left borders or bottom borders are valid. Since the case with points located on the cell vertices is complicated, we define valid vertex points for each cell separately. Each cell has its record of language distributions.

### Team members: 
* [Xinyi Jin (Melody)](https://www.linkedin.com/in/melody-jin/)

* [Yan Ying (Eliza)](https://www.linkedin.com/in/yan-ying-602848218/)

<p align="right">(<a href="#top">back to top</a>)</p>


### Built With

* [Spartan](https://dashboard.cloud.unimelb.edu.au)
* [mpi4py](https://mpi4py.readthedocs.io/en/stable/)
* [Shapely](https://shapely.readthedocs.io/en/stable/manual.html)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Spartan access

    * should have access to Spartan project
    * make a symbolic link to Tweet and locaional files to user directory,
    E.g. 
    ```sh
    ln –s /data/projects/COMP90024/bigTwitter.json 
    ln –s /data/projects/COMP90024/smallTwitter.json 
    ln –s /data/projects/COMP90024/tinyTwitter.json 
    ln –s /data/projects/COMP90024/sydGrid.json
    ```


### Installation

Clone the repo
   ```sh
   git clone https://github.com/MelodyJIN-Y/Tweet-language-distribution
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

#### Process bigTwitter.json file on Spartan: 
* case 1: 1 node and 1 core 
   ```sh
   sbatch 1node1core.slurm
   ```
   
* case 2: 1 node and 8 cores
   ```sh
   sbatch 1node8core.slurm
   ```
      
* case 3: 2 nodes and 8 cores (with 4 cores per node)
    
   ```sh
   sbatch 2node8core.slurm
   ```
      
### Files 
Functionalities of back-end multiprocessing programs are to to collect tweets, transmit AURIN data, and do sentiment analysis concurrently. Thus, under the "back-end" folder, there are three separate folders consist of their corresponding programs. Within each folder, execution can starts by using "python" command on the main program. The following commands show how to run main functions. Since the overall design of the back-end system is complexed, some more details are described in another [README.md](https://github.com/MelodyJIN-Y/Liveability-of-Melbourne/blob/main/backend/README.md) file under the "backend" folder.
#### [src folder](https://github.com/MelodyJIN-Y/Tweet-language-distribution/tree/main/src): slurm files to specify computing recources
   * main.py: the main multi-processing functions
      
   * Utility.py: A class for count language distribution based on defined rules 
      
   * plot_result.py: a helper function for performance comparisons of different computing resources 


#### [slurm folder](https://github.com/MelodyJIN-Y/Tweet-language-distribution/tree/main/slurm): slurm files to specify computing recources
   * 1 node and 1 core: 1node1core.slurm
      
   * 1 node and 8 cores: 1node8core.slurm
      
   * 2 nodes and 8 cores (with 4 cores per node): 2node8core.slurm
   

#### [output folder](https://github.com/MelodyJIN-Y/Tweet-language-distribution/tree/main/output): all the collected results

   * Resources usage output: 
   
      * 1node1core.out
      
      * 1node8core.out
      
      * 2node8core.out
   * Language ditribution of the bigTwitter.json file:
   
      * bigTwitter_result.csv
      

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GNU License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [README template](https://github.com/othneildrew/Best-README-Template)
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[contributors-url]: https://github.com//MelodyJIN-Y/Liveability-of-Melbourne/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[forks-url]: https://github.com//MelodyJIN-Y/Liveability-of-Melbourne/network/members
[license-shield]: https://img.shields.io/github/license/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[license-url]: https://github.com/MelodyJIN-Y/Liveability-of-Melbourne/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url-Melody]: https://www.linkedin.com/in/melody-jin/
[linkedin-url-Eliza]: linkedin.com/in/yan-ying-602848218
[linkedin-url-Budd]: https://www.linkedin.com/in/xinhao-hao-3a199b23a/
[linkedin-url-Liqin]: www.linkedin.com/in/liqin-zhang-1480ba1a2
[video-shield]: https://img.shields.io/youtube/channel/views/UCLdeGdBHXeT1GqU83WmMy0w?style=social
[product-screenshot]: images/webpage.png
