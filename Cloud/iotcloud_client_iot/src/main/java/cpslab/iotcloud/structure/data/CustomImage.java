package cpslab.iotcloud.structure.data;


public class CustomImage {
    public String path;
    public double n_pole; // orientation diff between real area n angle and layout n angle

    public CustomImage(String path, double n_pole) {
        this.path = path;
        this.n_pole = n_pole;
    }
}
