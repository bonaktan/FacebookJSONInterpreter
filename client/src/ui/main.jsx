import React from "react";
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";

import FolderFetch from './Home/FolderFetch'
import Messages from "./Messages/main";
export default function FacebookJSONInterpreter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<Header />}>
                    <Route index element={<FolderFetch />} />
                    <Route path='messages' element={<Messages />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

const Header = () => { return (
    <>
        <div>
            <div><p>Facebook JSON Interpreter</p></div>
            <div><p>Made By: bonnybonnybonaktan</p></div>
        </div>
        <br />
        <Outlet />
    </>
)}