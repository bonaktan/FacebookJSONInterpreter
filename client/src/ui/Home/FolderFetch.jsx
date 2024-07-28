import React, {useContext} from 'react';
import GlobalVariables from '../../globals/globalVariables';
import { useNavigate } from 'react-router-dom';
import {useUpdateEffect, sleep} from '../../api/utils';
function FolderFetch() {
    // make them talk first dumbass
    const Globals = useContext(GlobalVariables)
    const {apiSendRequest, apiReturnData, apiInProgress} = Globals
    let navigate = useNavigate()
    function setPath(event) {
        event.preventDefault()
        apiSendRequest({"requestType": "setFilePath", "path": event.target[0].value})
        navigate('/messages')
    }

    return (
        <>
            <p>Due to security/compatibility restrictions browsers placed on us, we cannot show a directory picker at this moment.</p>
            <p>Please type the full directory of the UNCOMPRESSED Facebook Data you downloaded</p>
            <form onSubmit={setPath} action='/messages' target='_blank'>
                <input type='text'/>
                <button type='submit'disabled={apiInProgress}>Submit</button>
            </form>
            <p>{apiInProgress ? 'Parsing. Please wait.' : ''}</p>
        </>
    );
}

export default FolderFetch;
