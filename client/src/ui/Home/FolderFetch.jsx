import React, {useContext, useState} from 'react';
import GlobalVariables from '../../globals/globalVariables';
import { useNavigate } from 'react-router-dom';
function FolderFetch() {
    // make them talk first dumbass
    const Globals = useContext(GlobalVariables)
    const navigate = useNavigate()
    const [directory, setDirectory] = useState('')
    const [inProgress, setInProgress] = useState(false)
    const api = Globals.API
    async function submitDirectory () {
        setInProgress(true)
        await api.post('', {'requestType': 'setFilePath', 'path': directory}).then(
            (respo) => {
                if (respo.data['returnType'] == 'error') {console.error(respo)}
                else (navigate('/messages'))
            }
        )
    }
    return (
        <>
            <p>Due to security/compatibility restrictions browsers placed on us, we cannot show a directory picker at this moment.</p>
            <p>Please type the full directory of the UNCOMPRESSED Facebook Data you downloaded</p>
            <span>
                <input type='text' value={directory} onChange={(e) => setDirectory(e.target.value)}/>
                <button onClick={submitDirectory}>Submit</button>
            </span>
            <p>{inProgress ? 'Loading, Please Wait.' : ''}</p>
        </>
    );
}

export default FolderFetch;
