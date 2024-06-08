import React from 'react';
import usePythonSocketBare from '../api/websocket';
/**
 * Contains General Layout for the Site, with the API Hookk
 * @return {JSXElementConstructor} General Layout of Site
 * */
function FacebookJSONInterpreter() {
    // eslint-disable-next-line no-unused-vars
    const {handleClickSendMessage, readyState} = usePythonSocketBare();
    handleClickSendMessage('Hello');
    return <p>{''+readyState}</p>;
}

export {FacebookJSONInterpreter};
