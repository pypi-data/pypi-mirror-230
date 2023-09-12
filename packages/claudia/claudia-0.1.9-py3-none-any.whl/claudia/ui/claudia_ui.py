import os
import shlex
import subprocess
import time

import streamlit as st
from PIL import Image
from claudia.claudia import *
from claudia.ui.ui_helper import create_account, send_payment_across_accounts, mint_nft, burn_nft, \
    create_nft_buy_offer, accept_nft_buy_offer, accept_nft_sell_offer, create_nft_sell_offer
from streamlit_option_menu import option_menu


st.set_page_config(layout='wide')
set_to_project_root_wd()
st.title('Claudia')
st.caption('XRPL No-Code Automation Framework')


def execute(cmd):
    split_cmd = shlex.split(cmd)
    popen = subprocess.Popen(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, split_cmd)


def launch_console_and_execute(cmd):
    st.markdown(
        '''
        <style>
        .streamlit-expanderHeader {
            background-color: #000000;
            color: #FFFFFF;
            font-family: "Lucida Console", "Courier New", monospace;
        }
        .streamlit-expanderContent {
            background-color: #000000;
            color: #FFFFFF;
            font-family: "Lucida Console", "Courier New", monospace;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )

    with st.expander("Details", expanded=True):
        try:
            for path in execute(cmd):
                st.text(path)

            st.success('Successfully completed the task.')
        except Exception as e:
            st.error('Something went wrong.')


def launch_console_and_display(message):
    st.markdown(
        '''
        <style>
        .streamlit-expanderHeader {
            background-color: #000000;
            color: #FFFFFF;
            font-family: "Lucida Console", "Courier New", monospace;
        }
        .streamlit-expanderContent {
            background-color: #000000;
            color: #FFFFFF;
            font-family: "Lucida Console", "Courier New", monospace;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )

    with st.expander("Details", expanded=True):
        try:
            st.text(message)
            st.success('Successfully completed the task.')
        except Exception as e:
            st.error('Something went wrong.')


def click_learning_path_network_button():
    st.toast("click_learning_path_network_button has been called")
    if 'clicked_learning_path_network_button' not in st.session_state:
        st.session_state.clicked_learning_path_network_button = True
    st.toast(
        f"st.session_state.clicked_learning_path_network_button: {st.session_state.clicked_learning_path_network_button}")


with st.sidebar:
    image = Image.open('./ui/logo.png')
    st.image(image)

    sidebar_selection = option_menu(
        "Claudia",
        ["Home", "Custom XRPL Networks", 'XRPL Tests', 'XRPL Learning Center', 'Settings'],
        icons=['house', 'cpu', "cpu", 'binoculars', 'book', 'gear'],
        menu_icon="balloon",
        default_index=0,
        key=1
    )

if sidebar_selection == "Home":
    with st.container():
        st.write("Welcome to Claudia!")
        st.markdown(
            'Claudia is a helper utility that allows users to perform XRPL specific tasks both locally and on other '
            'public networks. More information can be found at [Claudia\'s PyPi homepage]'
            '(https://pypi.org/project/claudia/). '
        )
        st.balloons()
elif sidebar_selection == "Custom XRPL Networks":
    with st.container():
        network_menu = option_menu(
            sidebar_selection,
            [
                "Build rippled",
                "Install rippled",
                "Start Network",
                "Stop Network",
                "Network Status",
                "Build Witness Server",
                "Start Sidechain Network",
                "Stop Sidechain Network",
                "Check Witness Server Status",
                "Deploy Network to Cloud"
            ],
            icons=[
                'building-gear',
                'building-check',
                'play',
                'stop',
                'eyeglasses',
                'building-gear',
                'play',
                'stop',
                'eyeglasses',
                'cloud'
            ],
            menu_icon="balloon",
            default_index=0
        )
        if network_menu == "Build rippled":
            form = st.form(key='build_rippled_form')
            form.text('Build rippled using Claudia...')
            repo = form.text_input('Enter the absolute path to the rippled repo', placeholder='e.g. /Users/me/rippled')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                if not os.path.isabs(repo) or not os.path.exists(repo):
                    st.error('Valid absolute repo path must be provided! Please try again.')
                else:
                    with st.spinner(
                            'Building rippled. Please do not navigate away, close the tab or refresh the page '
                            'until the task has finished.'):
                        launch_console_and_execute(get_launch_command_rippled_build(repo))
        elif network_menu == "Install rippled":
            form = st.form(key='install_rippled_form')
            form.text('Install rippled using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Installing rippled. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_rippled_install())
        elif network_menu == "Start Network":
            form = st.form(key='start_network_form')
            form.info('Please make sure you have built/installed rippled using Claudia prior to running this step.')
            form.text('Start Local Network using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Starting Local Network. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_network_start())
        elif network_menu == "Stop Network":
            form = st.form(key='stop_network_form')
            form.text('Stop Local Network using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Stopping Local Network. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_network_stop())
        elif network_menu == "Network Status":
            form = st.form(key='check_network_status_form')
            form.info('Please make sure you have built/installed rippled using Claudia prior to running this step.')
            form.text('Check the status of the Local Network using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Checking Local Network Status. Please do not '
                        'navigate away, close the tab or refresh the page until the task has finished.'):
                    launch_console_and_execute(get_launch_command_network_status())
        elif network_menu == "Build Witness Server":
            form = st.form(key='build_witness_server_form')
            form.text('Build Witness Server using Claudia...')
            repo = form.text_input('Enter the absolute path to the Witness Server repo',
                                   placeholder='e.g. /Users/me/xbridge_witness')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                if not os.path.isabs(repo) or not os.path.exists(repo):
                    st.error('Valid absolute repo path must be provided! Please try again.')
                else:
                    with st.spinner(
                            'Building witness server. Please do not navigate away, close the tab or refresh the page '
                            'until the task has finished.'):
                        launch_console_and_execute(get_launch_command_witness_build(repo))
        elif network_menu == "Start Sidechain Network":
            form = st.form(key='start_sidechain_network_form')
            form.info('Before you run this steps, please make sure you have:')
            form.info('   1. built/installed rippled')
            form.info('   2. started local network')
            form.info('   3. built witness server')
            form.text('Start Sidechain Network using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Starting Sidechain Network. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_sidechain_start())
        elif network_menu == "Stop Sidechain Network":
            form = st.form(key='stop_sidechain_network_form')
            form.text('Stop Sidechain Network using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Stopping Sidechain network. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_sidechain_stop())
        elif network_menu == "Check Witness Server Status":
            form = st.form(key='check_witness_server_status')
            form.info('Please make sure you have built the witness server using Claudia prior to running this step.')
            form.text('Check the status of the Witness Server using Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Checking Witness Server status. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_witness_status())
        elif network_menu == "Deploy Network to Cloud":
            st.info("Coming soon...")
elif sidebar_selection == "XRPL Tests":
    with st.container():
        test_menu = option_menu(
            sidebar_selection,
            ["Run System Tests", "Run Unit Tests"],
            icons=['building', "boxes"],
            menu_icon="balloon",
            default_index=0
        )
        if test_menu == "Run Unit Tests":
            form = st.form(key='unit_test_form')
            form.text('Run Unit Tests using Claudia...')
            filter = form.text_input('OPTIONAL: Enter the test filter.', placeholder='e.g. ripple.tx.Offer')
            form.info("If no filter is applied, all unit tests will be executed. This can take a while.")
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Running Unit Tests. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_run_unit_tests(filter))
        elif test_menu == "Run System Tests":
            st.text('Run System Tests using Claudia...')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                lib = st.radio(
                    'Choose client language',
                    ('py', 'js'))
            with col2:
                if lib == "py":
                    client_type = st.radio(
                        'Choose client type',
                        ('jsonrpc', 'websocket'))
                    invalidate_cache = 'false'
                else:
                    client_type = "websocket"
                    invalidate_cache = st.radio(
                        'Invalidate cache?',
                        ('true', 'false'))
            with col3:
                network = st.radio(
                    'Choose network',
                    ('local-mainnet', 'devnet', 'testnet', 'local-sidechain'))
            with col4:
                tag = st.radio(
                    'Choose test tag',
                    ('smoke', 'regression', 'time_intensive'))
            with col5:
                feature = st.radio(
                    'Choose feature',
                    ('payments', 'trustline', 'nft_burn_mint', 'all'))

            yes_button = st.button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Running System Tests. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    try:
                        explorer_msg = f'Click [here]({get_explorer_url(network)}) to open explorer...'
                        st.markdown(explorer_msg, unsafe_allow_html=True)
                        setup_system_test_env(lib, client_type, network, tag, feature, invalidate_cache)
                        launch_console_and_execute(get_launch_command_system_test_tests(lib, tag, feature))
                        teardown_system_test_env(lib)
                    except Exception as e:
                        set_to_project_root_wd()
                        raise e
elif sidebar_selection == "XRPL Learning Center":
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            learning_center_menu = option_menu(
                sidebar_selection,
                [
                    "Create an Account",
                    "Send a Payment",
                    "Mint an NFT",
                    "Burn an NFT",
                    "Create an NFT Buy Offer",
                    "Accept an NFT Buy Offer",
                    "Create an NFT Sell Offer",
                    "Accept an NFT Sell Offer"
                ],
                icons=[
                    'book',
                    'book',
                    'book',
                    'book',
                    'book',
                    'book',
                    'book',
                    'book'
                ],
                menu_icon="balloon",
                default_index=0
            )

        with col2:
            if learning_center_menu == "Create an Account":
                create_account()
            elif learning_center_menu == "Send a Payment":
                send_payment_across_accounts()
            elif learning_center_menu == "Mint an NFT":
                mint_nft()
            elif learning_center_menu == "Burn an NFT":
                burn_nft()
            elif learning_center_menu == "Create an NFT Buy Offer":
                create_nft_buy_offer()
            elif learning_center_menu == "Accept an NFT Buy Offer":
                accept_nft_buy_offer()
            elif learning_center_menu == "Create an NFT Sell Offer":
                create_nft_sell_offer()
            elif learning_center_menu == "Accept an NFT Sell Offer":
                accept_nft_sell_offer()
elif sidebar_selection == "Settings":
    with st.container():
        settings_menu = option_menu(
            sidebar_selection,
            [
                "Set Install Mode",
                "Enable a rippled feature",
                "Disable a rippled feature",
                "Cleanup",
                "List System Requirements",
                "List System Test features",
                "Print rippled version"
            ],
            icons=[
                'gear',
                'gear',
                'gear',
                'gear',
                'gear',
                'gear',
                'gear'
            ],
            menu_icon="balloon",
            default_index=0
        )

        if settings_menu == "List System Requirements":
            form = st.form(key='list_system_requirements_form')
            form.text('List System Requirements for running Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Listing System Requirements. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_display(get_launch_command_system_requirements_message())
        elif settings_menu == "List System Test features":
            form = st.form(key='list_system_tests_features_form')
            form.text('List features available with System Tests...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Checking all the feature available with System Tests. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_display(get_launch_command_system_test_features_message())
        elif settings_menu == "Print rippled version":
            form = st.form(key='print_rippled_version_form')
            form.text('Print rippled version installed/built by Claudia...')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Checking rippled version. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_rippled_version())
        elif settings_menu == "Cleanup":
            form = st.form(key='cleanup_form')
            form.text('Perform system cleanup using Claudia...')
            form.warning(
                "WARNING!! Running this command will wipe out everything built by Claudia. This action cannot be "
                "undone.")
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        'Performing system cleanup. Please do not navigate away, close the tab or refresh the page '
                        'until the task has finished.'):
                    launch_console_and_execute(get_launch_command_clean())
        elif settings_menu == "Enable a rippled feature":
            form = st.form(key='enable_rippled_feature_form')
            form.text('Enable a rippled feature using Claudia...')
            feature = form.text_input('Enter the rippled feature name', placeholder='e.g. DIDoc')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        f"Attempting to enable '{feature}' feature. Please do not navigate away, close the tab or refresh the page "
                        f"until the task has finished."):
                    launch_console_and_execute(get_launch_command_enable_feature(feature))
        elif settings_menu == "Disable a rippled feature":
            form = st.form(key='disable_rippled_feature_form')
            form.text('Disable a rippled feature using Claudia...')
            feature = form.text_input('Enter the rippled feature name', placeholder='e.g. DIDoc')
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        f"Attempting to disable '{feature}' feature. Please do not navigate away, close the tab or refresh the page "
                        f"until the task has finished."):
                    launch_console_and_execute(get_launch_command_disable_feature(feature))
        elif settings_menu == "Set Install Mode":
            form = st.form(key='set_install_mode_form')
            form.text('Set the install mode to "build" or "install"...')
            mode = form.radio(
                'Choose the install mode',
                ('Build', 'Install'))
            yes_button = form.form_submit_button(label='GO!')
            if yes_button:
                with st.spinner(
                        f"Setting the install mode to {mode}. Please do not navigate away, close the tab or refresh the page "
                        f"until the task has finished."):
                    if mode == "Build":
                        launch_console_and_execute(get_launch_command_set_install_mode_to_build())
                    elif mode == "Install":
                        launch_console_and_execute(get_launch_command_set_install_mode_to_install())
