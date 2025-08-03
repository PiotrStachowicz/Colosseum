/* App.tsx
*
* This module concentrates page's content
* */
import {BrowserRouter, HashRouter, Route, Routes} from "react-router-dom";

import HomePage from "./pages/HomePage";
import ChessPage from "@/pages/ChessPage";
import ReversiPage from "@/pages/ReversiPage";
import JunglePage from "@/pages/JunglePage";

function App() {
    return (
        <HashRouter>
            <Routes>
                <Route path='/' element={<HomePage />}/>
                <Route path='/chess' element={<ChessPage />}/>
                <Route path='/reversi' element={<ReversiPage />}/>
                <Route path='/jungle' element={<JunglePage />}/>
            </Routes>
        </HashRouter>
    )
}

export default App
