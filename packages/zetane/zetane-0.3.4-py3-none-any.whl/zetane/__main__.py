#INSTALL WITH: pip3 install -e .
#after navigating into api directory
# and then do pip3 install .
import sys
from dotenv import find_dotenv, load_dotenv
import os
from zetane import Protector

def main():
    load_dotenv(find_dotenv(usecwd=True))

    args = sys.argv[1:]
    args = [x.lower() if args[args.index(x) - 1] != '-k' else x for x in args]
    if len(args) == 0:
        return print("That's our name :)")

    if '-h' in args or '--h' in args or 'help' in args: #HELP MENU OF COMMANDS BIG PRINT STATEMENT
        return '''
        \033[1mHELP\033[1m
        \033[1mUSAGE\033[1m
        $ zetane --help

        \033[1mOPTIONS\033[1m
        -h, help, \t help will always be given at Zetane to those who ask for it
        -k \t\t user API key
        -o \t\t selected organization for command
        -p \t\t selected project for command and
        ls, list \t list all available models or datasets pertaining to a project or organization
        -m \t\t is either the filepath for file uploads or model name for report creation
        -d \t\t is either the filepath for file uploads or dataset name for report creation
        -t \t\t is either the filepath for the test_series JSON file for report creation
        -f \t\t for continuous logging output during report generation

        \033[1mCOMMANDS\033[1m
        upload \t\t uploads a model or dataset file to a project & organization
        create \t\t schedules a report creation for chosen a model and dataset

        \033[1mAPI KEYS\033[1m
        API keys can either be stored in a .env file local to your api files under the alias API_KEY,
        or they can be passed following the argument, -k

        \033[1mEXAMPLES\033[1m
        $ zetane upload -o <organization> -p <project> -m <model_local_filepath> -k <api_key>
        $ zetane upload -o <organization> -p <project> -d <dataset_local_filepath> -m <model_local_filepath>

        $ zetane list -o <organization> -p <project> datasets
        $ zetane ls -o <organization> -p <project> models
        $ zetane report_status -o <organization> -p <project> -n <name>

        $ zetane create -o <organization> -p <project> -d <dataset_name> -m <model_name> -t <test_series_local_filepath>

        The format for a test.json profile is:
        {
            "blur": {
                "intervals": "3",
                "max": "5",
                "min": "3"
        },
            "elastic transform": {
                "intervals": "5",
                "max": "4",
                "min": "2",
                "xai": []
            }
        }

        ** when entering <names> that contain spaces, please use quotation marks around the name **

        Happy Using!
        '''
    API_KEY = False
    if "API_KEY" in os.environ:
        API_KEY = os.getenv("API_KEY")
    if '-k' in args: #API KEY
        API_KEY = args[args.index('-k')+1]
    if not API_KEY:
        return print('Please include API_KEY.')

    protector = Protector(API_KEY)

    if '-p' not in args or '-o' not in args:
        return print('''
        Please include an organization and associated project in your command using the following tags:
        -o <organization> -p <project>
        ''')
    org = args[args.index('-o')+1]
    proj = args[args.index('-p')+1]
    protector.config(project=proj, org=org)

    if 'ls' in args or 'list' in args:
        if 'models' in args or 'model' in args:
            res = protector.get_entries('models', org, proj)
            listType = 'models'
        elif 'datasets' in args or 'dataset' in args:
            res = protector.get_entries('datasets', org, proj)
            listType = 'datasets'
        else:
            return print('Please select to view either models or datasets.')

        if res == None:
            return print(f"Failed to fetch list of {listType} :'(")
        print(f'List of {listType}:')
        for elem in res.json():
            print('\t- ' + elem['filename'])
        return

    if 'report_status' in args:
        if not ('-n' in args):
            return print('Please include report name')
        report_name = args[args.index('-n')+1]
        return protector.getReportStatus(org, proj, report_name)

    if 'create' in args and '-m' in args and '-d' in args and '-t' in args:
        dataset = args[args.index('-d')+1]
        model = args[args.index('-m')+1]
        test_profile_path = args[args.index('-t')+1]
        return protector.report(org, proj, model, dataset, test_profile_path, (False if '-f' in args else True))
    elif 'upload' in args and ('-m' in args or '-d' in args):
        if '-m' in args:
            modelPath = args[args.index('-m')+1]
            protector.upload_model(modelPath, org, proj)
        if '-d' in args:
            datasetPath = args[args.index('-d')+1]
            protector.upload_dataset(datasetPath, org, proj)
    else:
        print(f'''
        Failed to {'create report' if 'create' in args else 'upload information'} due to invalid or missing information
        Command format to create a report is:
        zetane {'create' if 'create' in args else 'upload'} -o <org> -p <project> -m <model> -d <dataset> -t <test_profile> -k <api_key>
        Tagged arguments may be entered in any order
        ''')


    if 'filepath' in args:
        filepath = args[args.index('filepath') + 1] if len(args) > 1 else ''
        print(os.path.abspath(filepath))

if __name__ == '__main__':
    main()
