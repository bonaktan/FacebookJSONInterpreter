import React from 'react';
import usePythonSocketBare from '../api/websocket';
/**
 * Contains General Layout for the Site, with the API Hookk
 * @return {JSXElementConstructor} General Layout of Site
 * */
function FacebookJSONInterpreter() {
    // eslint-disable-next-line no-unused-vars
    const {ready, socket, send} = usePythonSocketBare();
    return <p>{''+ready}</p>;
}

export {FacebookJSONInterpreter};
