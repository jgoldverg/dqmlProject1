package sona.cse460.Sona460.model;

import javax.persistence.*;
import java.util.Date;

@Entity
@Table(name="days")
public class OneDayCovid {

    @Id
    @Temporal(TemporalType.DATE)
    private Date date;

    @Id
    @GeneratedValue
    private Long id;


}
