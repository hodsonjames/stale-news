# Runs entire data path provided initial input files are named correctly
# Permission Command: chmod +x run.sh
# Run Command: ./run.sh

python clean.py
python extract_news.py
python merge_market.py
python extract_reg_data.py
