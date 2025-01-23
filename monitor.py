import os
import time
import subprocess
import sys
import shutil
import logging

# Set up logging to log into log.txt
log_filename = 'log.txt'

# Create or append to the log file
if not os.path.exists(log_filename):
    with open(log_filename, 'w') as f:
        pass  # Create an empty log file if it doesn't exist

logging.basicConfig(
    filename=log_filename, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Monitor directory and file extension
MONITOR_DIR = "./"  # Monitor the current directory, or adjust the path as needed
FILE_EXTENSION = ".json"
IGNORED_FILES = {"output.json", "output_updated.json"}  # Files to be ignored

# Control whether to enable the graph building feature
ENABLE_GRAPH_BUILDING = True  # Set to False to disable the graph building feature

def build_graph():
    """Call build3.py to build the graph, ensuring that the graph is built before starting monitoring."""
    try:
        logging.info("Starting graph construction...")
        subprocess.run([sys.executable, "build3.py"], check=True)
        logging.info("Graph construction completed!")
        return True  # Graph construction successful
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred during graph construction: {e}")
        return False  # Graph construction failed

def rename_output_file(original_filename):
    """Rename output_updated.json to <original filename>-prd.json."""
    output_file = "output_updated.json"
    if os.path.exists(output_file):
        # Remove the extension from the processed filename and add the -prd suffix
        new_filename = f"{os.path.splitext(original_filename)[0]}-prd.json"
        shutil.move(output_file, new_filename)  # Rename the file
        logging.info(f"Renamed {output_file} to {new_filename}")
        return new_filename
    return None

def monitor_directory():
    """Monitor newly added JSON files in the directory."""
    
    # Add a separator to mark the start of a new monitoring session
    logging.info("=" * 50)
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logging.info(f"Starting directory monitor at {start_time}...")

    # If graph building is enabled, perform graph construction first
    if ENABLE_GRAPH_BUILDING:
        if not build_graph():
            print("图谱构建失败，无法启动目录监控。")
            logging.error("Graph construction failed, unable to start directory monitoring.")
            logging.info("=" * 50)  # End session here
            return  # Exit if graph construction fails

    # Build a list of known files for the first round
    known_files = {filename for filename in os.listdir(MONITOR_DIR) if filename.endswith(FILE_EXTENSION)}
    print(f"已知文件列表构建完成，初始文件数: {len(known_files)}")
    logging.info(f"Initial known files list built, initial file count: {len(known_files)}")

    while True:
        # Get all JSON files in the current directory
        current_files = {filename for filename in os.listdir(MONITOR_DIR) if filename.endswith(FILE_EXTENSION)}

        # Handle removed files
        removed_files = known_files - current_files
        for filename in removed_files:
            print(f"文件 {filename} 已被删除，从已知文件列表中移除。")
            logging.info(f"File {filename} has been deleted, removed from known files list.")
            known_files.remove(filename)

        # Handle newly added files
        new_files = current_files - known_files
        for filename in new_files:
            if filename in IGNORED_FILES:
                print(f"文件 {filename} 被检测到，但已跳过处理（不处理特定文件）。")
                logging.info(f"File {filename} detected but skipped (ignored file).")
                continue  # Skip specific files

            file_path = os.path.join(MONITOR_DIR, filename)
            print(f"检测到新文件: {filename}")
            logging.info(f"Detected new file: {filename}")

            try:
                # Run query.py with the new file
                query_result = subprocess.run(
                    [sys.executable, "query.py", file_path],
                    capture_output=True,
                    text=True
                )
                if query_result.returncode != 0:
                    print(f"运行 query.py 时出错: {query_result.stderr}")
                    logging.error(f"Error running query.py: {query_result.stderr}")
                    continue

                # Redirect output to exchange.py
                exchange_result = subprocess.run(
                    [sys.executable, "exchange.py", query_result.stdout],
                    capture_output=True,
                    text=True
                )
                if exchange_result.returncode != 0:
                    print(f"运行 exchange.py 时出错: {exchange_result.stderr}")
                    logging.error(f"Error running exchange.py: {exchange_result.stderr}")
                    continue

                # Use the output from exchange.py as input for insert.py
                insert_result = subprocess.run(
                    [sys.executable, "insert.py"],
                    input=exchange_result.stdout,
                    capture_output=True,
                    text=True
                )
                if insert_result.returncode != 0:
                    print(f"运行 insert.py 时出错: {insert_result.stderr}")
                    logging.error(f"Error running insert.py: {insert_result.stderr}")
                    continue

                print(f"处理文件 {filename} 完成，输出已更新.")
                logging.info(f"Processing of file {filename} complete, output updated.")

                # Rename output_updated.json file to <processed filename>-prd.json
                renamed_file = rename_output_file(filename)
                if renamed_file:
                    # Skip further processing for the renamed file
                    known_files.add(renamed_file)
                    print(f"新生成文件 {renamed_file} 跳过后续处理。")
                    logging.info(f"New generated file {renamed_file} skipped from further processing.")

            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {e}")
                logging.error(f"Error occurred while processing file {filename}: {e}")

            # Add the file to the known files list
            known_files.add(filename)

        # Check every 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    monitor_directory()
