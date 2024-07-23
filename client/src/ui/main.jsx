import React, {useContext} from 'react';
import GlobalVariables from '../globals/globalVariables';

function FacebookJSONInterpreter() {
    // make them talk first dumbass
    const Globals = useContext(GlobalVariables)
    const {apiSendRequest, apiReturnData, apiInProgress, requestData} = Globals
    function setPath(event) {
        event.preventDefault()
        apiSendRequest({"requestType": "setFilePath", "path": event.target[0].value})
        console.debug(requestData)
    } 
    return (
        <>
            <p>Due to security/compatibility restrictions browsers placed on us, we cannot show a directory picker at this moment.</p>
            <p>Please type the full directory of the UNCOMPRESSED Facebook Data you downloaded</p>
            <form onSubmit={setPath} target='_blank'>
                <input type='text'/>
                <button type='submit'>Submit</button>
            </form>
            <p>{apiInProgress}</p>
            <p>{JSON.stringify(apiReturnData)}</p>
        </>
    );
}

export {FacebookJSONInterpreter};
