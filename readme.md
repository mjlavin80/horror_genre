Click on any .ipynb file to render it in Github. The Notebook files with something worth seeing so far are:

1. [Analysis of Walker's Dictionary and "Walker Ratios" of Underwood Corpus](https://github.com/mjlavin80/horror_genre/blob/master/Walker's%20Dictionary.ipynb)
2. [Approximate Reproduction of Underwood-Sellers Dictionary.com Results](https://github.com/mjlavin80/horror_genre/blob/master/Dictionary.com%20Results.ipynb)
3. [OED Cross-Validation] (https://github.com/mjlavin80/horror_genre/blob/master/OED%20Results.ipynb)
4. [Perhaps Overly Lengthy Explanation of OED Webscraping and Normalization] (https://github.com/mjlavin80/horror_genre/blob/master/oed_normalize.ipynb)

Eventually I will also update the "Machine Learning" notebook with various results. 

Notes for Reacreating the Entire Repo and Running .py files:
1. Git clone entire repo
2. Use virtual environment to install dependencies (requirements.txt file coming soon). Note: .py files run in Python 2, .ipynb are upcoded to Python 3. (Sorry! I know this is lame, and I will fix it soon.)
3. Edit "sample_config.py" to point to your database of choice and rename to "config.py"
4. Build db by running "db_create.py", then "underwood_metadata.py", "underwood_dictcom.py", "underwood_oed.py" and "underwood_counts.py" (Depends upon files downloaded from "The Stone and the Shell" blog  
5. Execute various scripts once db is built. Scripts are generally designed to store results in sqlite databases, so existing .db files may raise conflicts. 
