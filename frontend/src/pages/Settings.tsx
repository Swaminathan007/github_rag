
import { useState } from "react"
export default function Settings() {
    const [llm_settings, setLlmSettings] = useState(null)



    const init = () => {
        fetch("/api/v1/llm/settings")
            .then((res) => res.json())
            .then((data) => {
                setLlmSettings(data)
            })
    }
    return (
        <div>
            <h1>Settings</h1>
        </div>
    )
}