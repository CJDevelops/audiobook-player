import os
import json
import vlc
import time


# Global variables

CURRENT_BOOK_JSON = "current_book.json"
CURRENT_POSITION_JSON = "current_position.json"
LIBRARY_JSON = "library.json"
LIBRARY_LOCATION = r"E:\Audiobooks MP3"


def clear_screen():
    """
    Clear the terminal screen.

    This function first prints a message indicating that the screen is being cleared.
    Then, it uses the 'os.system' function to clear the terminal based on the operating system.
    On Windows (nt), the 'cls' command is used to clear the screen. On other systems, 'clear' is used.

    Note:
    - This function should work on most Unix-based systems (Linux, macOS) and Windows.

    Returns:
        None
    """
    print("Clearing")  # Print a message indicating that the screen is being cleared
    # Clear the terminal screen based on the OS
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(milliseconds):
    # Convert milliseconds to seconds and get the remaining milliseconds
    seconds, milliseconds = divmod(milliseconds, 1000)
    # Convert seconds to minutes and get the remaining seconds
    minutes, seconds = divmod(seconds, 60)
    # Convert minutes to hours and get the remaining minutes
    hours, minutes = divmod(minutes, 60)
    # Return the formatted time as HH:MM:SS
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def load_audiobook_library(library_file=LIBRARY_JSON, override=False):
    """
    Load the audiobook library from a JSON file or create a new one if the file doesn't exist.

    Args:
        library_file (str): The path to the JSON file containing the library data.
                            Default value is LIBRARY_JSON, which should be defined elsewhere.
        override (bool): If True, the function will always create a new library and override the existing file.
                         If False and the file exists, the library will be loaded from the file.

    Returns:
        dict: The audiobook library as a dictionary.
    """
    if os.path.exists(library_file) and not override:
        # If the library file exists and the override flag is False, load the library from the file.
        with open(library_file, "r") as file:
            library = json.load(file)
    else:
        # If the library file does not exist or the override flag is True, create a new library.
        library = create_audiobook_library()

        # Save the newly created library to the JSON file.
        with open(library_file, "w") as file:
            json.dump(library, file)

    return library


def create_audiobook_library(root_dir=LIBRARY_LOCATION):
    """
    Create an audiobook library from the files and directories in the specified root directory.

    Args:
        root_dir (str): The root directory path to start building the audiobook library.
                        Default value is LIBRARY_LOCATION, which should be defined elsewhere.

    Returns:
        dict: The audiobook library as a nested dictionary with paths to audio files and cover art images.
    """
    audiobook_library = {}

    mp3_counter = 1

    for entry in os.scandir(root_dir):
        full_path = entry.path
        name = entry.name

        if entry.is_dir():
            # If it's a directory, create a sub-dictionary and populate it recursively.
            sub_dict = create_audiobook_library(full_path)
            audiobook_library[name] = sub_dict
        elif name.endswith(".jpg"):
            # If it's an image file, store its path under the key 0 in the current dictionary.
            audiobook_library[0] = full_path
        elif name.endswith(".mp3"):
            # If it's an audio file, store its path under a key (mp3_counter) in the current dictionary.
            audiobook_library[mp3_counter] = full_path
            mp3_counter += 1

    return audiobook_library


def play_chapter(chapter_file_path, chapter_id, start_timestamp=0):
    """
    Play an audiobook chapter using the VLC media player library.

    Args:
        chapter_file_path (str): The file path of the audiobook chapter.
        chapter_id (int): The ID of the chapter being played.
        start_timestamp (int, optional): The timestamp (in milliseconds) to start playback from.
                                         Default value is 0, indicating the start of the chapter.

    Returns:
        None
    """
    def print_current_status(timestamp, duration):
        clear_screen()
        print(f"Currently playing: Chapter {chapter_id} in {book_title} by {author}")
        print(f"{format_time(timestamp)} / {format_time(duration)}")

    # Cleanup resources after chapter playback
    def cleanup():
        player.stop()
        instance.release()
        # Optionally, perform any other cleanup actions here

    # Extract author and book title from the chapter file path
    author, book_title = [chapter_file_path.split("\\")[2], chapter_file_path.split("\\")[-2]]

    # Create a new VLC instance and media player
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(chapter_file_path)
    player.set_media(media)

    # Start playback from the specified timestamp
    player.play()
    player.set_time(start_timestamp)
    time.sleep(1)

    try:
        while player.is_playing():
            # Update current position and display playback information
            current_media = player.get_media()
            if current_media is not None:
                current_timestamp = player.get_time()
                total_duration = player.get_length()
                print_current_status(current_timestamp, total_duration)

                # Write the current timestamp to current_position.json
                with open(CURRENT_POSITION_JSON, 'w') as file:
                    json.dump({"chapter_id": chapter_id,
                              'timestamp': current_timestamp}, file)

            time.sleep(0.1)
    except KeyboardInterrupt:
        # Handling user interruption by keyboard (Ctrl+C)
        cleanup()
        main_menu()
    finally:
        cleanup()
        print("Chapter playback completed.")


def keep_listening():
    """
    Resume playing the audiobook from the last stopped position.

    Steps:
    1. Load the current position and current book from their respective JSON files.
    2. Play the book from the current position, with a 5-second backward offset.

    Note:
    - The current position is stored in CURRENT_POSITION_JSON.
    - The current book details are stored in CURRENT_BOOK_JSON.

    Returns:
    None
    """
    # Step 1: Load the current position and current book from their JSON files.
    with open(CURRENT_POSITION_JSON, 'r') as file:
        current_position = json.load(file)

    with open(CURRENT_BOOK_JSON, 'r') as file:
        current_book = json.load(file)

    # Step 2: Play the book from the current position, with a 5-second backward offset.
    starting_chapter = current_position['chapter_id']
    timestamp = max(0, current_position['timestamp'] - 5000)
    play_book(book=current_book, starting_chapter=starting_chapter, timestamp=timestamp)


def select_book():
    """
    Allow the user to select an audiobook or series to play.

    Returns:
        None
    """
    def is_series(item):
        return any(isinstance(value, dict) for value in item.values())

    # Step 1: Load the audiobook library
    library = load_audiobook_library()

    # Step 2: Display the available options to the user
    print("Available Books and Series:")
    options = [(author, book_or_series, chapters_or_books)
               for author, books_or_series in library.items()
               for book_or_series, chapters_or_books in books_or_series.items()]

    for idx, (author, book_or_series, _) in enumerate(options, start=1):
        print(f"{idx:02d}. {book_or_series} by {author}")

    # Step 3: Ask the user to select a book or series by number
    selected_number = input("Enter the number of the book or series you want to play: ")

    try:
        selected_number = int(selected_number)
        selected_author, selected_book_or_series, chapters_or_books = options[selected_number - 1]
    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid number.")
        return

    # Step 4: Check if the selection is a series or a single book
    if is_series(chapters_or_books):
        # This is a series, show the books in the series and ask the user to select a book
        print(f"Selected Series: {selected_book_or_series}")
        books_options = list(chapters_or_books.items())

        for idx, (book, _) in enumerate(books_options, start=1):
            print(f"{idx:02d}. Book: {book}")

        selected_book_number = input("Enter the number of the book you want to play: ")

        try:
            selected_book_number = int(selected_book_number)
            selected_book_or_series, selected_chapters = books_options[selected_book_number - 1]
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")
            return
    else:
        # This is a single book
        selected_chapters = chapters_or_books

    # Save the selected book's chapters to the CURRENT_BOOK_JSON file
    with open(CURRENT_BOOK_JSON, 'w') as file:
        json.dump(selected_chapters, file)

    # Play the selected book's chapters, starting from the beginning (chapter 1)
    play_book(book=selected_chapters, starting_chapter=1)


def play_book(book, starting_chapter=1, timestamp=0):
    """
    Play the audiobook from the specified chapter and timestamp.

    Args:
        book (dict): The audiobook as a dictionary, where keys are chapter numbers and values are file paths.
        starting_chapter (int): The chapter number from which to start playing the audiobook.
                                Default value is 1, indicating the beginning of the book.
        timestamp (int): The timestamp (in milliseconds) from which to start playing each chapter.
                         Default value is 0, indicating the start of the chapter.

    Returns:
        None
    """
    for chapter_number, chapter_file_path in book.items():
        if int(chapter_number) < int(starting_chapter):
            # Skip chapters before the starting chapter.
            continue

        play_chapter(chapter_file_path=chapter_file_path, chapter_id=chapter_number, start_timestamp=timestamp)

        # Reset the timestamp for the next chapter to start from the beginning.
        timestamp = 0


def recreate_library():
    """
    Recreate the audiobook library by loading the library data and overriding the existing data.

    Returns:
        None
    """
    load_audiobook_library(override=True)
    print("The library has been recreated. Returning to the main menu.")


def exit_app():
    """
    Exit the audiobook app gracefully.

    Returns:
        None
    """
    print("Exiting the audiobook app. Goodbye!")
    quit()


def main_menu():
    """
    Display the main menu of the audiobook app and allow users to choose different options.

    Returns:
        None
    """
    # Create a dictionary to map user choices to corresponding functions
    menu_options = {
        "1": keep_listening,
        "2": select_book,
        "3": recreate_library,
        "4": exit_app
    }

    # Load current position and current book data
    with open(CURRENT_POSITION_JSON, 'r') as file:
        current_position = json.load(file)
        chapter_id = current_position['chapter_id']

    with open(CURRENT_BOOK_JSON, 'r') as file:
        current_book = json.load(file)
        book_string = current_book[chapter_id]
        author, book_title = [book_string.split("\\")[2], book_string.split("\\")[-2]]

    # A loop to keep the menu running until the user chooses to exit
    while True:
        # Display the main menu options after clearing the screen.
        clear_screen()
        print("\n===== Main Menu =====")
        print(f"1. Keep Listening - {format_time(current_position['timestamp'])} of Chapter {chapter_id} in {book_title} by {author}")
        print("2. Select Book")
        print("3. Recreate Library")
        print("4. Exit")

        # Get user input for their choice
        choice = input("Enter the option number: ")

        # Check if the user's choice is a valid option in the dictionary
        if choice in menu_options:
            clear_screen()
            # Call the corresponding function using the dictionary
            menu_options[choice]()
        else:
            print("Invalid choice. Please select a valid option (1-4).")


if __name__ == "__main__":
    main_menu()
