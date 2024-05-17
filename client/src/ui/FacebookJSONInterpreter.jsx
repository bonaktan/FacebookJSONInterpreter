import React from 'react';
import apiCore from '../api/api';
// Function: link api to client, then do ui and shits
function FacebookJSONInterpreter() {
    const api = apiCore();
    return (
        <>
            <p>tite</p>
            <input/>
            <button onClick={api.send()}>Submit</button>
        </>);
}

export default FacebookJSONInterpreter;
