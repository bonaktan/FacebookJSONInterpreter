import React from 'react';
import ReactDOM from 'react-dom/client';

import FacebookJSONInterpreter from './ui/main.jsx';
import {GlobalVariableProvider} from './globals/globalVariables.js'
import './globals/index.css';

/**
 * Starting Point of FacebookJSONInterpreter,
 * Contains Global Vars and Bullshits
 */
function main() {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
        <GlobalVariableProvider>
            <FacebookJSONInterpreter/>
        </GlobalVariableProvider>
    );
}

main();
