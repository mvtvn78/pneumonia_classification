import axios from "axios";
import { URL_PREDICT } from "../utils/constant";

const predictAPI:any = async (formData:any)=>{
   try{
        const res = await axios.post(URL_PREDICT,formData);
        return res.data;
   }
   catch(err)
   {
        return undefined;
   }
} 
export default predictAPI;