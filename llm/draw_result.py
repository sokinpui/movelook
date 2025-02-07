import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load JSON files from a directory
def load_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as f:
                json_data = json.load(f)
                # Append data to the list
                data.append(json_data)
    return data

# Function to process the loaded data
def process_data(data):
    tokens = []
    durations = []
    sample_sizes = []

    for entry in data:
        sample_size = entry.get('sample_size', 0)
        for log, details in entry.items():
            if log != 'sample_size':
                tokens.append(details['total_tokens'])
                durations.append(float(details['duration'].replace('s', '')))
                sample_sizes.append(sample_size)

    return pd.DataFrame({
        'tokens': tokens,
        'duration': durations,
        'sample_size': sample_sizes
    })

# Function to plot the relationships
def plot_tokens_vs_sample_size(df):
    # Average tokens for the same sample size
    avg_tokens_per_sample_size = df.groupby('sample_size')['tokens'].mean().reset_index()

    # Plotting tokens vs sample size
    plt.scatter(avg_tokens_per_sample_size['sample_size'], avg_tokens_per_sample_size['tokens'], color='blue')
    plt.title('Average Tokens vs Sample Size')
    plt.xlabel('Sample Size')
    plt.ylabel('Average Tokens')
    plt.grid()

    plt.savefig('average_tokens_vs_sample_size.png')

    plt.tight_layout()
    plt.show()

def plot_tokens_vs_duration(df):
    # Plotting duration vs tokens
    # plt.scatter(df['tokens'], df['duration'], color='green')
    df_filtered = df[df['duration'] < 100]  # Adjust the threshold as needed
    sns.scatterplot(data=df_filtered, x='tokens', y='duration', alpha=0.6, s=50, color='green')
    sns.regplot(data=df_filtered, x='tokens', y='duration', scatter=False, color='red', line_kws={'linewidth': 2})
    plt.title('Duration vs Tokens')
    plt.xlabel('Total Tokens')
    plt.ylabel('Duration (s)')
    plt.grid()

    plt.savefig('duration_vs_tokens_full_picture.png')

    plt.tight_layout()
    plt.show()

    df_filtered = df_filtered[df_filtered['tokens'] < 128000]  # Adjust the threshold as needed

    sns.scatterplot(data=df_filtered, x='tokens', y='duration', alpha=0.6, s=50, color='green')
    sns.regplot(data=df_filtered, x='tokens', y='duration', scatter=False, color='red', line_kws={'linewidth': 2})
    plt.title('Duration vs Tokens')
    plt.xlabel('Total Tokens')
    plt.ylabel('Duration (s)')
    plt.grid()

    plt.savefig('duration_vs_tokens.png')

    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    directory = 'output'  # Change this to your directory path
    json_data = load_json_files(directory)
    df = process_data(json_data)
    plot_tokens_vs_sample_size(df)
    plot_tokens_vs_duration(df)
