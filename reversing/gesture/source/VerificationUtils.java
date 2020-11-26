import java.util.*; 
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.SecretKeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;
import java.io.UnsupportedEncodingException;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
 
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.IvParameterSpec;

public class VerificationUtils
{
	public static char p_array[] = { 'g', 'o', '0', 'd', '$', 'l', 'u', 'c', 'k' };
	public static byte[] CHECK_SALT = new byte[] { (byte)0xde, (byte)0xad, (byte)0xbe, (byte)0xef };
	public static byte[] DECRYPT_SALT = new byte[] { (byte)0x11, (byte)0x22, (byte)0x33, (byte)0x44};
	public static String encryption_iv = "pJoKGZlx+tbr38ooZGNYeg==";
	public static String encrypted_flag = "ajVD6Q7SS9ma7ghrOEG1Z1Tn0+RBlK/Rhntt4QVI8Iq0K6HZxkEfvVpnFk9utep2";
	public static String inds2str(int[] ar)
	{
		StringBuilder s = new StringBuilder();
		for (int k = 0; k < ar.length && ar[k] != -1; k++)
			s.append(p_array[ar[k]]);
		return s.toString();
	}
	public static byte[] check(int[] circles)
	{
		int[] values = new int[9];
		for (int i = 0; i < 9; i++) values[i] = -1;
		for (int i = 0; i < 9; i++)
			if (circles[i] != -1)
				values[circles[i]] = i;
		String s = inds2str(values);
		//System.out.println("pbkdf2(" + s + ") = " + toHex(pbkdf2(s, CHECK_SALT)));
		if (toHex(pbkdf2(s, CHECK_SALT)).equals("8045a9b6d9eece98352e353c9091f353"))
		{
			// correct
			return pbkdf2(s, DECRYPT_SALT); // decrypt_key
		}
		else
		{
			// wrong
			return null;
		}
	}
	private static String toHex(byte[] data)
	{
		StringBuilder s = new StringBuilder();
		for (int i = 0; i < data.length; i++)
			s.append(String.format("%02x", data[i]));
		return s.toString();
	}
	public static byte[] pbkdf2(String password, byte[] salt)
	{
		try
		{
			PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, 1500, 128);
			SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
			return skf.generateSecret(spec).getEncoded();
		}
		catch (NoSuchAlgorithmException e)
		{
			System.out.println("[-] No such algorithm");
			return null;
		}
		catch (InvalidKeySpecException e)
		{
			System.out.println("[-] No such keyspec");
			return null;
		}
	}
	/*
	public static String encrypt_flag(String flag, byte[] key)
	{
		try
		{
			SecretKeySpec skeyspec = new SecretKeySpec(key, "AES");
			IvParameterSpec ivspec = new IvParameterSpec(Base64.getDecoder().decode(encryption_iv));
			Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
			cipher.init(Cipher.ENCRYPT_MODE, skeyspec, ivspec);
			return Base64.getEncoder().encodeToString(cipher.doFinal(flag.getBytes("US-ASCII"))).replace("\n","").replace("\r","");
		}
		catch (Exception e)
		{
			e.printStackTrace(System.out);
			return e.toString();
		}
	}
	*/
	public static String decrypt_flag(byte[] key)
	{
		try
		{
			SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
			Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
			IvParameterSpec ivspec = new IvParameterSpec(Base64.getDecoder().decode(encryption_iv));
			cipher.init(Cipher.DECRYPT_MODE, secretKey, ivspec);
			return new String(cipher.doFinal(Base64.getDecoder().decode(encrypted_flag)));
		}
		catch (Exception e)
		{
			return e.toString();
		}
	}
}
