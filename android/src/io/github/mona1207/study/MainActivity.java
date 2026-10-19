package io.github.mona1207.study;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Base64;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private WebView web;
    private ProgressBar progress;
    private LinearLayout errorPanel;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private ValueCallback<Uri[]> fileCallback;
    private byte[] pendingExport;
    private long lastCheck = -1, promptedVersion = 0;
    private boolean checking;
    private static final int FILE_PICK = 31, SAVE_EXPORT = 32;
    private final String exportScript = "(function(){if(window.__monaExportPatched)return;window.__monaExportPatched=true;"
        + "function save(a){if(!a||!a.hasAttribute('download')||!(/^(blob:|data:)/.test(a.href)))return false;"
        + "fetch(a.href).then(r=>r.blob()).then(b=>{if(b.size>50331648)throw Error('备份超过48MB，请分批导出图片');"
        + "var f=new FileReader();f.onload=()=>MonaApp.exportFile(a.download||'学习备份.json',b.type||'application/octet-stream',String(f.result).split(',')[1]);f.readAsDataURL(b)})"
        + ".catch(e=>alert('导出未完成：'+e.message));return true}"
        + "var original=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(!save(this))original.call(this)};"
        + "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[download]');if(save(a)){e.preventDefault();e.stopPropagation()}},true);})();";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(247,248,243));
        root.setOnApplyWindowInsetsListener((v,insets)->{if(android.os.Build.VERSION.SDK_INT>=30){android.graphics.Insets bars=insets.getInsets(android.view.WindowInsets.Type.systemBars());v.setPadding(bars.left,bars.top,bars.right,bars.bottom);}else v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets;});
        web = new WebView(this);
        root.addView(web,new FrameLayout.LayoutParams(-1,-1));
        progress = new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);
        root.addView(progress,new FrameLayout.LayoutParams(-1,dp(3)));
        errorPanel = new LinearLayout(this);
        errorPanel.setOrientation(LinearLayout.VERTICAL);errorPanel.setGravity(android.view.Gravity.CENTER);errorPanel.setPadding(dp(28),dp(28),dp(28),dp(28));errorPanel.setBackgroundColor(Color.rgb(247,248,243));
        TextView title=new TextView(this);title.setText("暂时无法连接教材");title.setTextSize(22);title.setTextColor(Color.rgb(50,80,59));errorPanel.addView(title);
        TextView copy=new TextView(this);copy.setText("请检查网络后重试，已保存的学习记录仍保留在本机。");copy.setTextSize(14);copy.setPadding(0,dp(16),0,dp(20));errorPanel.addView(copy);
        Button retry=new Button(this);retry.setText("重新连接");retry.setOnClickListener(v->{errorPanel.setVisibility(View.GONE);web.loadUrl(UpdatePolicy.HOME+"?app=android&t="+System.currentTimeMillis()+"#home");});errorPanel.addView(retry);
        errorPanel.setVisibility(View.GONE);root.addView(errorPanel,new FrameLayout.LayoutParams(-1,-1));
        setContentView(root);getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        if(android.os.Build.VERSION.SDK_INT>=33)getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,()->handleBack());
        WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);settings.setDatabaseEnabled(true);settings.setAllowFileAccess(false);settings.setAllowContentAccess(true);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);settings.setTextZoom(100);settings.setSupportZoom(true);settings.setBuiltInZoomControls(true);settings.setDisplayZoomControls(false);settings.setMediaPlaybackRequiresUserGesture(true);settings.setUserAgentString(settings.getUserAgentString()+" MonaStudy/"+appVersion());
        CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);
        web.addJavascriptInterface(new Bridge(),"MonaApp");
        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){String url=request.getUrl().toString();if(UpdatePolicy.trustedPage(url)&&!url.endsWith(".apk"))return false;openExternal(url);return true;}
            @Override public void onPageStarted(WebView v,String url,android.graphics.Bitmap icon){progress.setVisibility(View.VISIBLE);}
            @Override public void onPageFinished(WebView v,String url){progress.setVisibility(View.GONE);if(UpdatePolicy.trustedPage(url))v.evaluateJavascript(exportScript,null);}
            @Override public void onReceivedError(WebView v,WebResourceRequest r,WebResourceError e){if(r.isForMainFrame())errorPanel.setVisibility(View.VISIBLE);}
            @Override public void onReceivedHttpError(WebView v,WebResourceRequest r,WebResourceResponse e){if(r.isForMainFrame()&&e.getStatusCode()>=400)errorPanel.setVisibility(View.VISIBLE);}
        });
        web.setWebChromeClient(new WebChromeClient(){
            @Override public void onProgressChanged(WebView v,int value){progress.setProgress(value);if(value>=100)progress.setVisibility(View.GONE);}
            @Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> callback,FileChooserParams params){if(fileCallback!=null)fileCallback.onReceiveValue(null);fileCallback=callback;try{startActivityForResult(params.createIntent(),FILE_PICK);}catch(Exception e){fileCallback.onReceiveValue(null);fileCallback=null;toast("无法打开文件选择器");}return true;}
        });
        web.setDownloadListener((url,ua,disposition,mime,length)->openExternal(url));
        if(state==null||web.restoreState(state)==null)web.loadUrl(UpdatePolicy.HOME+"?app=android&t="+System.currentTimeMillis()+"#home");
    }

    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private String appVersion(){try{return getPackageManager().getPackageInfo(getPackageName(),0).versionName;}catch(Exception e){return "1.0.0";}}
    private void toast(String message){Toast.makeText(this,message,Toast.LENGTH_LONG).show();}
    private void openExternal(String url){try{Uri uri=Uri.parse(url);if("https".equalsIgnoreCase(uri.getScheme())||"http".equalsIgnoreCase(uri.getScheme())||"mailto".equalsIgnoreCase(uri.getScheme()))startActivity(new Intent(Intent.ACTION_VIEW,uri));else toast("无法打开此链接");}catch(Exception e){toast("没有可打开此链接的应用");}}
    private boolean trusted(){return web!=null&&UpdatePolicy.trustedPage(web.getUrl());}

    private class Bridge {
        @JavascriptInterface public void checkForUpdates(){runOnUiThread(()->{if(trusted())checkUpdate(true);});}
        @JavascriptInterface public void finishHome(){runOnUiThread(()->{if(trusted())finish();});}
        @JavascriptInterface public void exportFile(String name,String mime,String content){
            if(content==null||content.length()>67108864)return;
            runOnUiThread(()->{if(!trusted())return;if(pendingExport!=null){toast("请先完成当前文件保存");return;}worker.execute(()->{
                try{byte[] bytes=Base64.decode(content,Base64.DEFAULT);runOnUiThread(()->{if(isFinishing())return;pendingExport=bytes;Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT);save.addCategory(Intent.CATEGORY_OPENABLE);save.setType(mime!=null&&mime.contains("/")?mime:"application/octet-stream");save.putExtra(Intent.EXTRA_TITLE,UpdatePolicy.exportName(name));try{startActivityForResult(save,SAVE_EXPORT);}catch(Exception e){pendingExport=null;toast("无法打开保存位置，请使用浏览器导出");}});}catch(Exception e){runOnUiThread(()->toast("文件生成失败，请重试"));}
            });});
        }
    }

    private void checkUpdate(boolean manual){
        if(checking||(!manual&&lastCheck>=0&&SystemClock.elapsedRealtime()-lastCheck<300000))return;
        checking=true;lastCheck=SystemClock.elapsedRealtime();worker.execute(()->{
            try{
                HttpURLConnection connection=(HttpURLConnection)new URL(UpdatePolicy.MANIFEST+"?t="+System.currentTimeMillis()).openConnection();connection.setConnectTimeout(12000);connection.setReadTimeout(12000);connection.setUseCaches(false);connection.setInstanceFollowRedirects(false);connection.setRequestProperty("Cache-Control","no-cache");
                JSONObject android;
                try{if(connection.getResponseCode()!=200)throw new Exception("版本服务暂不可用");try(InputStream input=connection.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] buffer=new byte[4096];int n;while((n=input.read(buffer))!=-1){if(out.size()+n>65536)throw new Exception("版本信息无效");out.write(buffer,0,n);}android=new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8)).getJSONObject("android");}}finally{connection.disconnect();}
                long offered=android.optLong("version_code",0),installed=getPackageManager().getPackageInfo(getPackageName(),0).versionCode;String label=android.optString("version_name"),notes=android.optString("notes","更新功能和体验"),download=UpdatePolicy.safeDownload(android.optString("download_url"));
                runOnUiThread(()->{checking=false;if(isFinishing())return;if(UpdatePolicy.newVersion(installed,offered)&&(manual||promptedVersion!=offered)){promptedVersion=offered;new AlertDialog.Builder(this).setTitle("发现新版本 "+label).setMessage(notes+"\n\n将打开下载地址，安装时由 Android 确认；请覆盖安装以保留本机记录。").setPositiveButton("下载更新",(d,w)->openExternal(download)).setNegativeButton("稍后",null).show();}else if(manual)toast("当前 App 已是最新版本 "+appVersion());});
            }catch(Exception e){runOnUiThread(()->{checking=false;if(manual)toast("暂时无法检查更新，请稍后重试");});}
        });
    }

    @Override public void onBackPressed(){handleBack();}
    private void handleBack(){
        if(!trusted()){if(web.canGoBack())web.goBack();else finish();return;}
        web.evaluateJavascript("(async()=>{try{if(document.querySelector('.v27-select-menu')){window.dispatchEvent(new Event('mona-close-menu',{cancelable:true}));return}var dialog=document.querySelector('dialog[open]');if(dialog){dialog.dispatchEvent(new Event('cancel',{cancelable:true}));return}if(!location.hash||location.hash==='#home'){await window.monaPrepareUpdate?.();MonaApp.finishHome()}else if(/^#(settings|graph)$/.test(location.hash)&&window.monaGoHome)window.monaGoHome();else if(window.monaNativeBack)window.monaNativeBack();else history.back()}catch(e){alert('草稿尚未保存，请稍后再返回。')}})()",null);
    }
    @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();checkUpdate(false);}
    @Override protected void onPause(){if(web!=null){web.evaluateJavascript("window.dispatchEvent(new Event('zhixu-flush-ink'));",null);web.onPause();}super.onPause();}
    @Override protected void onSaveInstanceState(Bundle out){if(web!=null)web.saveState(out);super.onSaveInstanceState(out);}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==FILE_PICK){if(fileCallback!=null){fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(result,data));fileCallback=null;}}else if(request==SAVE_EXPORT){byte[] bytes=pendingExport;pendingExport=null;if(result==RESULT_OK&&data!=null&&data.getData()!=null&&bytes!=null){Uri uri=data.getData();worker.execute(()->{try(OutputStream out=getContentResolver().openOutputStream(uri)){if(out==null)throw new Exception();out.write(bytes);runOnUiThread(()->toast("文件已保存"));}catch(Exception e){runOnUiThread(()->toast("保存未完成，请重试"));}});}}}
    @Override protected void onDestroy(){if(fileCallback!=null)fileCallback.onReceiveValue(null);worker.shutdown();if(web!=null){((ViewGroup)web.getParent()).removeView(web);web.destroy();}super.onDestroy();}
}
