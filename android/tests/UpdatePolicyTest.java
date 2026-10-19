import io.github.mona1207.study.UpdatePolicy;
public class UpdatePolicyTest {
 public static void main(String[] args){
  require(UpdatePolicy.trustedPage("https://mona1207.github.io/discrete-math/?v=27#home"));
  for(String url:new String[]{"http://mona1207.github.io/discrete-math/","https://mona1207.github.io.evil.test/discrete-math/","https://evil.test/discrete-math/","https://mona1207.github.io:444/discrete-math/","https://mona1207.github.io/other/","javascript:alert(1)","https://user@mona1207.github.io/discrete-math/"})require(!UpdatePolicy.trustedPage(url));
  require(UpdatePolicy.newVersion(1,2));require(!UpdatePolicy.newVersion(2,2));require(!UpdatePolicy.newVersion(2,1));require(!UpdatePolicy.newVersion(2,Long.MAX_VALUE));
  require(UpdatePolicy.safeDownload("https://mona1207.github.io/discrete-math/download/mona-study-1.0.1.apk").endsWith("1.0.1.apk"));
  require(UpdatePolicy.safeDownload("https://evil.test/malware.apk").equals(UpdatePolicy.DOWNLOAD));
  require(UpdatePolicy.exportName("../笔记/备份.json").equals(".._笔记_备份.json"));
  System.out.println("PASS Android update version ordering, HTTPS origin, download allowlist and export filename handling.");
 }
 private static void require(boolean ok){if(!ok)throw new AssertionError();}
}
