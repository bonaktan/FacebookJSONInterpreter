import React, {useContext} from "react";
import GlobalVariables from "../../globals/globalVariables";
export default function Messages() {
    const Globals = useContext(GlobalVariables)
    const {apiSendRequest, apiReturnData, apiInProgress} = Globals
    if (apiInProgress) { return (<p>Loading...</p>); }
    return (
        <>{JSON.stringify(apiReturnData)}</>
    )
}