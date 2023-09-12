# Florida County Parcel Data Collector

## Description

This project focuses on automating the downloading, formatting, and storing of parcel data for various counties in Florida. It integrates with ARCGIS for some counties and uses other data sources for the rest.

## Features

- Supports multiple counties: Charlotte, Lee, Manatee, etc.
- Downloads both zip and CSV files.
- Integration with ARCGIS for additional data sources.
- Configurable data storage paths.
- Efficiently maps data to county-specific schemas.

## Installation

1. Clone the repository:

   ``` bash
   git clone https://github.com/your_username/your_repository_name.git
   ```

2. Install the required packages:

   ``` bash
   pip install -r requirements.txt
   ```

3. Set up environmental variables:

   ``` bash
   cp .env.example .env
   ```

   Fill in the required variables in `.env`.

## Usage

1. For ARCGIS counties:

   ``` bash
   python arcgis_downloader.py
   ```

2. For other counties:

   ``` bash
   python downloader.py
   ```

3. To test the system:

   ``` bash
   python tester.py
   ```

## Dependencies

- pandas
- arcgis
- urllib
- zipfile

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See `LICENSE` for more information.
