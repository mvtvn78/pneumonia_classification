import GlitchText from "../assets/components/GlitchText"
import Magnet from "../assets/components/Magnet";
import TrueFocus from "../assets/components/TrueFocus";
import '../assets/css/App.css'
import VariableProximity from "../assets/components/VariableProximity";
import { useRef, useState } from "react";
import GradientText from "../assets/components/GradientText";
import CircularGallery from "../assets/components/CircularGallery";
import SpotlightCard from "../assets/components/SpotlightCard";
import Reveal from "../assets/components/Reveal";
import Upload from "../modal/Upload";
import LightRays from "../assets/components/LightRays";
import { Atom } from "react-loading-indicators";
import { CLASS_PRED } from "../utils/constant";
type Prediction = {
  msg: string;
  status: number;
  org: string;
  pred: number;
};
const App: React.FC<{}> = ({ }) => {
  const containerRef = useRef(null);
  const [loading,setLoading] = useState(false);
  const [modalUpload,setModalUpload] = useState(false);
  const [image,setImage] = useState("file_1760920639.939278.png")
  const [pred,setPred] = useState<Prediction| null>(null)
  return (
    <>
    {loading &&  <div style={{
    position:'fixed',
    width:'100%',
    height:'100%',
    backgroundColor:'rgba(255, 255, 255, 0.2)',
    display:'flex',
    justifyContent:'center',
    alignItems:'center',
    zIndex:'10000000'
  }}>
    <Atom color={["#ff0022", "#a1ff00", "#00ffdd", "#5e00ff"]} size="large"  />
  </div>}
    <div style={{ width: '100%', height: '500px', position: 'relative' }}>
    {!pred && <LightRays
    raysOrigin="top-center"
    raysColor="#00ffff"
    raysSpeed={0.8}
    lightSpread={1.2}
    rayLength={1.0}
    followMouse={true}
    mouseInfluence={0.1}
    noiseAmount={0.1}
    distortion={0.05}
    className="custom-rays"
  />}
  
    <div style={{ position: 'absolute', top: 0,left: 0 ,right: 0, bottom:0}}>
      <div className="header" style={{position:'fixed',width:'100%',background:'rgba(0, 0, 0, 0.3)'}}>
        <div className="bar_wrap" style={{padding :'20px'}}>
        <div style={{
            display :'flex',
            alignItems:'center',
          }}>
          <div style={{
              marginRight : 'auto'
              }}>
            <GlitchText
              speed={1.2}
              enableShadows={true}
              className='fs35x'
              >
            pneumonia classfication
            </GlitchText>
          </div>
          <div>
            <Magnet padding={50} disabled={false} magnetStrength={1}>
            <a href="https://github.com/mvtvn78/pneumonia_classification" target="_blank" className='fs24x'>
                <div style={{
                  color:'white',
                  display : 'flex'
                }}> 
                    Repo trên&nbsp;
                    <p style={{
                      color:'rgb(0, 240, 255)'
                    }}>Github</p>
                </div>
            </a>  
            </Magnet>
          </div>
        </div>
        </div>
      </div>
      <div className="main" style={{paddingTop:'100px'}}>
      <Reveal index_Delay={0.16} >  
        <div className="detection cl_white sect_margin">
              <div style={{display:'flex',justifyContent:'center',gap:'40px'}}>
                <div style={{display:'flex',alignItems:'center'}}>
                  <div className="content"> 
                  <h1 className="cl_blue" style={{textTransform:'uppercase'}}>Phát hiện viêm phổi</h1>
                    <h3 style={{marginBottom:'50px',marginTop:'20px'}}>Tải lên tấm ảnh x-quang ngực để xem dự đoán </h3>
                    <div style={{marginBottom:'40px'}}>
                      <TrueFocus 
                      sentence="Normal Pneumonia"
                      manualMode={false}
                      blurAmount={5}
                      borderColor="white"
                      animationDuration={2}
                      pauseBetweenAnimations={1}
                      />
                      </div>
                  <button style={{fontSize:'30px'}} onClick={()=>setModalUpload(true)}>
                    <GradientText 
                        colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                        animationSpeed={3}
                        showBorder={true}
                        className="p_button"
                          >
                      Tải lên
                      </GradientText>
                  </button>
                  </div>
                </div>
                <div>
                  <img style={{
                    objectFit:'contain',
                    height:'400px'
                  }} src={image} alt="" id="image-output"/>
                  {pred  &&  <div className="predict">
                    <p style={{margin:'10px',fontSize:'20px',fontWeight:'bolder'}}>Kết quả dự đoán</p>
                    {pred?.pred ==0  &&  <div style={{backgroundColor:'#0a8e28',textAlign:'center'}}>Phổi bạn được dự đoán bình thường</div>   }
                    {pred?.pred >0 && pred?.pred <3 && <div style={{backgroundColor:'#FA0204',textAlign:'center'}}>Phổi bạn được dự đoán viêm phổi và có thể tác nhân là {CLASS_PRED[pred?.pred]}</div> }          
                  </div>}
                </div>
              </div>
          </div>
      </Reveal>
        
      
    <Reveal index_Delay={0.24} >
    <div className="author sect_margin">
        <div className="author_title t_center fs_title t_upper" ref={containerRef}
              style={{position: 'relative'}}>
              <VariableProximity
                  label={'Sinh viên phát triển'}
                  className={'variable-proximity-demo cl_white' }
                  fromFontVariationSettings="'wght' 400, 'opsz' 9"
                  toFontVariationSettings="'wght' 1000, 'opsz' 40"
                  containerRef={containerRef}
                  radius={150}
                  falloff='linear'
              />
            </div>
        <div style={{display:'flex',justifyContent:'center',marginTop:'20px',gap:'50px'}}>
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
            <div className="cl_white">
            <div style={{display:'flex',justifyContent:'center'}}>
             <img src="Tvm_tn.jpg"  alt="" width={200} height={200} />
             </div>
              <h3 className="t_center p_10 t_upper">Sinh viên thực hiện</h3>
              <p className="t_center">Mai Văn Tiền</p>
            </div>
          </SpotlightCard>
          <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
            <div className="cl_white">
             <div style={{display:'flex',justifyContent:'center'}}>
              <img src="p1.jpg"  alt="" width={200} height={200} />
             </div>
              <h3 className="t_center p_10 t_upper">Sinh viên thực hiện</h3>
              <p className="t_center">Lê Huỳnh Cẩm Tú</p>
            </div>
          </SpotlightCard>
        </div>
        </div>
    </Reveal>
    <Reveal index_Delay={0.28} >
    <div className="sample">
          <div className="sample_title t_center fs_title t_upper" ref={containerRef}
                style={{position: 'relative'}}>
                <VariableProximity
                    label={'Các mẫu đã thực nghiệm'}
                    className={'variable-proximity-demo cl_white' }
                    fromFontVariationSettings="'wght' 400, 'opsz' 9"
                    toFontVariationSettings="'wght' 1000, 'opsz' 40"
                    containerRef={containerRef}
                    radius={150}
                    falloff='linear'
                />
              </div>
          <div style={{ height: '600px', position: 'relative' }}>
            <CircularGallery bend={1} textColor="#ffffff" borderRadius={0.05} />
          </div>
        </div>
    </Reveal>
       
     
      </div>
      <Upload show={modalUpload} setVisible={setModalUpload} setImage={setImage}   setPred={setPred} setLoading={setLoading} />
      {modalUpload && <button title="thoát" className="exit_modal" onClick={()=>{setModalUpload(false)}}>X</button>}
      </div>
    </div>
    </>
  )
};
export default App

