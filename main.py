import os
import json
import vlc
import time


# Globals

CURRENT_BOOK_JSON = "current_book.json"
CURRENT_POSITION_JSON = "current_position.json"
LIBRARY_JSON = "library.json"
LIBRARY_LOCATION = r"E:\Audiobooks MP3"

# Globals


def clear_screen():
    print("Clearing")
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def load_audiobook_library(library_file=LIBRARY_JSON, override=False):
    if os.path.exists(library_file) and not override:
        with open(library_file, "r") as f:
            library = json.load(f)
    else:
        library = create_audiobook_library()
        with open(library_file, "w") as f:
            json.dump(library, f)
    return library


def create_audiobook_library():
    audiobook_library = {}
    root_dir = LIBRARY_LOCATION

    def populate_library(path, current_dict):
        mp3_counter = 1
        for entry in os.scandir(path):
            full_path = entry.path
            name = entry.name
            if entry.is_dir():
                sub_dict = {}
                populate_library(full_path, sub_dict)
                current_dict[name] = sub_dict
            elif name.endswith(".jpg"):
                current_dict[0] = full_path
            elif name.endswith(".mp3"):
                current_dict[mp3_counter] = full_path
                mp3_counter += 1

    populate_library(root_dir, audiobook_library)
    return audiobook_library


def play_chapter(chapter_file_path, chapter_id, start_timestamp=0):

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
            current_media = player.get_media()
            if current_media is not None:
                clear_screen()

                author, book_title = [chapter_file_path.split(
                    "\\")[2], chapter_file_path.split("\\")[-2]]
                print(
                    f"Currently playing: Chapter {chapter_id} in {book_title} by {author}")

                timestamp = player.get_time()
                total_duration = player.get_length()
                print(f"{format_time(timestamp)} / {format_time(total_duration)}")
                # Write the current timestamp to current_position.json
                with open(CURRENT_POSITION_JSON, 'w') as file:
                    json.dump({"chapter_id": chapter_id,
                               'timestamp': timestamp}, file)

            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()
        instance.release()
        main_menu()

    # Chapter is over, do any necessary cleanup here
    player.stop()
    instance.release()

    print("Chapter playback completed.")


def keep_listening():
    # Step 1: Load the current position from current_position.json
    with open(CURRENT_POSITION_JSON, 'r') as file:
        current_position = json.load(file)

    with open(CURRENT_BOOK_JSON, 'r') as file:
        current_book = json.load(file)

    # Step 2: Play the book from the current position, 5s backwards offset
    play_book(book=current_book,
              starting_chapter=current_position['chapter_id'], timestamp=max(0, current_position['timestamp'] - 5000))


def select_book():

    def is_series(item):
        return any(isinstance(value, dict) for value in item.values())

    # Step 1: Load the audiobook library
    library = load_audiobook_library()

    # Step 2: Display the available options to the user
    print("Available Books and Series:")
    options = []
    for author, books_or_series in library.items():
        for book_or_series, chapters_or_books in books_or_series.items():
            options.append((author, book_or_series, chapters_or_books))
            print(f"{len(options):02d}. {book_or_series} by {author}")

    # Step 3: Ask the user to select a book or series by number
    selected_number = input(
        "Enter the number of the book or series you want to play: ")
    try:
        selected_number = int(selected_number)
        if selected_number < 1 or selected_number > len(options):
            raise ValueError
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    # Step 4: Find the corresponding book or series based on the selected number
    selected_author, selected_book_or_series, chapters_or_books = options[selected_number - 1]

    # Step 5: Check if the selection is a series or a single book
    if is_series(chapters_or_books):
        # This is a series, show the books in the series and ask the user to select a book
        print(f"Selected Series: {selected_book_or_series}")
        series_books = chapters_or_books
        print("Available Books in the Series:")
        books_options = []
        for book, chapters in series_books.items():
            books_options.append((book, chapters))
            print(f"{len(books_options)}. Book: {book}")

        selected_book_number = input(
            "Enter the number of the book you want to play: ")
        try:
            selected_book_number = int(selected_book_number)
            if selected_book_number < 1 or selected_book_number > len(books_options):
                raise ValueError
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Update the selected_book_or_series to the specific book in the series
        selected_book_or_series, selected_chapters = books_options[selected_book_number - 1]
    else:
        # This is a single book, get its chapters
        selected_chapters = chapters_or_books

    with open(CURRENT_BOOK_JSON, 'w') as file:
        json.dump(selected_chapters, file)

    play_book(book=selected_chapters, starting_chapter=1)


def play_book(book, starting_chapter=1, timestamp=0):
    for chapter_number, chapter_file_path in book.items():
        if int(chapter_number) < int(starting_chapter):
            continue
        play_chapter(chapter_file_path=chapter_file_path,
                     chapter_id=chapter_number, start_timestamp=timestamp)
        timestamp = 0


def recreate_library():
    load_audiobook_library(override=True)
    print("The library has been recreated. Returning to the main menu.")


def exit_app():
    print("Exiting the audiobook app. Goodbye!")
    quit()


def main_menu():
    # Create a dictionary to map user choices to corresponding functions
    menu_options = {
        "1": keep_listening,
        "2": select_book,
        "3": recreate_library,
        "4": exit_app
    }

    with open(CURRENT_POSITION_JSON, 'r') as file:
        current_position = json.load(file)
        chapter_id = current_position['chapter_id']

    with open(CURRENT_BOOK_JSON, 'r') as file:
        current_book = json.load(file)
        book_string = current_book[chapter_id]
        author, book_title = [book_string.split(
            "\\")[2], book_string.split("\\")[-2]]

    # A loop to keep the menu running until the user chooses to exit
    while True:
        # Display the main menu options after clearing the screen.
        clear_screen()
        print("\n===== Main Menu =====")
        print(
            f"1. Keep Listening - {format_time(current_position['timestamp'])} of Chapter {chapter_id} in {book_title} by {author}")
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
