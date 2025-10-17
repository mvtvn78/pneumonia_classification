import { FC, useRef, useState } from "react";
import '../assets/css/Upload.css';
import Swal from 'sweetalert2';
import predictAPI from "../services/predictApi";
import { DOMAIN_PUBLIC } from "../utils/constant";
interface UploadProps {
    show?: boolean,
    setVisible : Function,
    setImage : Function,
    setDetectList : Function
}
const  Upload: FC<UploadProps> = ({
    show = true,
    setVisible,
    setImage,
    setDetectList
})  =>{
    const callAPI = async(file:File) =>{
        setVisible(false);
        setDetectList([]);
        const formdata = new FormData();
        formdata.append("file",file);
        const data =  await predictAPI(formdata);
        if(data?.status == 0)
        {
            setImage(DOMAIN_PUBLIC+"/"+data?.org);
            const detectFaces:any = data?.detectFace;
            const detectList: any = data?.detectList;
            if(detectFaces.length > 0)
            {
                let idx = 0 ;
                const preData = detectFaces.map((val:string)=> {
                    const fake = (detectList[idx][0]*100).toFixed(2);
                    const real = (detectList[idx][1]*100).toFixed(2);
                    idx+=1;
                    return {"image":`${DOMAIN_PUBLIC}/${val}`,"Fake": fake,'Real':real};
                });
                setDetectList(preData)
            }
            return;
        }
        Swal.fire({
            title: "Tải file thất bại",
            icon: "warning"
          });
    }
    const intPutFile:any = useRef(null);
    const [textDetectDrag, setTextDetectDrag] = useState('Kéo và thả tệp vào đây');
    const dragContainer:any = useRef(null);
    const handleChangeFile = async(e:any) =>{
        e.preventDefault();
        const file = e.target.files[0];
        await callAPI(file);
    }
    const handleDropFile = async(e:any)=>{
        e.preventDefault();
        const fileObj = e.dataTransfer.files[0];
        if (dragContainer.current) {
          dragContainer.current.classList.remove('active');
        }
        setVisible(false);
        await callAPI(fileObj);
    }
    const handleOptionClick = () => {
        if(intPutFile.current)
            intPutFile.current.click();
    }
    const handleDragOver = (e:any) =>{
        e.preventDefault();
        setTextDetectDrag('Thả tệp để tải lên');
        if(dragContainer.current)
            dragContainer.current.classList.add('active');
    }
    const handleDragLeave = (e:any) =>{
        e.preventDefault();
        setTextDetectDrag('Kéo và thả tệp vào đây');
        if(dragContainer.current)
            dragContainer.current.classList.remove('active');
    }
    return (
        show &&  <div className="upload_wrap">
            <div className='upload_container'> 
        <div className="drag-area" ref={dragContainer} onDrop={handleDropFile} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
            <div className="icon"><i className="fas fa-cloud-upload-alt"></i></div>
            <header>{textDetectDrag}</header>
            <span>Hoặc</span>
            <button onClick={handleOptionClick}>Duyệt File</button>
            <input type="file" name="file" id="file" onChange={handleChangeFile} hidden ref={intPutFile}/>
        </div>
        </div>
        </div>
    )
}
export default Upload;