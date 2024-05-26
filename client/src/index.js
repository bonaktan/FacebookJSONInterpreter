import React from 'react';
import ReactDOM from 'react-dom/client';
import './ui/main.css';

import Header from './ui/Header.jsx'


function main() {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
        <Header/>
    );
}

main();
